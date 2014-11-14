# -*- coding: utf-8 -*-
from APIRequest import APIRequest
from gluon import current, HTTP


class APIKeyPermissions():
    def __init__(self, request):
        self.db = current.db
        self.request = request
        self.fields = self.request.vars["FIELDS"].split(",") if self.request.vars["FIELDS"] else []
        self.http_method = self.HTTPMethodWithName(self.request.env.request_method)
        self.hash = self.request.vars.API_KEY
        # =======================================================================
        # key pode ser nula ou ter as propriedades:
        #
        # dt_creation, active, user_id, group_role, group_id, max_requests, max_entries
        # total_requests
        # =======================================================================
        self.key = self.db(self.db.v_api_calls.auth_key == self.hash).select().first()
        self.tablename = APIRequest.controllerForRewritedURL() if not self.request.is_local else self.request.controller


    @staticmethod
    def HTTPMethodWithName(method):
        """
        Dado um determinado método, retorna o seu ID, caso o mesmo seja suportado pela API

        :param method: Uma string correspondente a um método HTTP
        :return: O id de um método
        :raise HTTP: 405 caso o método requisitado não seja suportado pela API
        """
        validMethod = current.db(current.db.api_methods.http_method == method).select(current.db.api_methods.id, cache=(
            current.cache.ram, 36000)).first()
        if validMethod:
            return validMethod.id
        else:
            raise HTTP(405, "Método requisitado não é suportado.")

    def canPerformAPICall(self):
        """
        Método responsável por verificar se a chave está ativa e a quantidade de requisições
        ainda não estrapolou o limite diário

        :rtype : bool
        :return: True se a chave estiver ativa e ainda puder fazer requisições. Caso contrário,
         Um erro HTTP relacionado ao erro é disparado
        :raise HTTP: 403 caso não tenha permissão de acessar uma coluna de uma tabela
        :raise HTTP: 429 caso tenha estrapolado o número máximo de requisições para o tipo de chave
        :raise HTTP: 403 se a chave não estiver mais ativa
        """
        if self.key.active:
            if (self.key.total_requests < self.key.max_requests):
                if self._hasPermissionToRequestFields():
                    return True
                else:
                    raise HTTP(403, "APIKey não possui permissão para acessar o recurso requisitado.")
            else:
                raise HTTP(429, "Número máximo de requisições esgotado.")
        else:
            raise HTTP(403, "Chave inativa")

    def _hasPermissionToRequestFields(self):
        """
        Caso FIELDS tenham sido especificados, verificará se existe alguma proibição
        de acesso a dados na tabela ou nas colunas requisitadas

        Caso FIELDS não tenha sido especificado, considera-se que a requisição deseja
        acessar a todo o conteúdo da tabela. Então, verifica-se se existe restrição em
        pelo menos uma das coluna da tabela

        * As consultas de permissão são cacheadas em 3600 segundos

        TODO converter tempo de cache para class constant

        :rtype : bool
        :return:
        """
        if len(self.fields) > 0:
            validFields = self._validateReturnFields(self.fields)
            hasPermission = self.db(
                self.conditionsToRequestContentFromTableColumns(self.tablename, validFields)).select(
                self.db.api_group_permissions.id,
                cache=(current.cache.ram, 3600))
            if hasPermission:
                return True
        else:
            hasPermission = self.db(self.conditionsToRequestAnyContentFromTable(self.tablename)).select(
                self.db.api_group_permissions.id,
                cache=(current.cache.ram, 3600))
            if hasPermission:
                return True
        return False


    # ===========================================================================
    # Método para verificar se os parâmetros de retorno passados são válidos
    #
    # Retorna uma lista com os FIELDS válidos ou uma lista vazia, que é interpretada
    # como todas as colunas
    # MÉTODO TAMBÉM EXISTEM EM APIRequest <<<<<< RESOLVER
    #===========================================================================
    def _validateReturnFields(self, fields):
        return [field for field in fields if field in current.dbSie[self.tablename].fields]

    def conditionsToRequestContentFromTableWithColumns(self, table, columns):
        return ( self.conditionsToRequestContentFromTable(table)
                 | self.conditionsToRequestContentFromTableColumns(table, columns) )

    #===========================================================================
    # Condição para proibição total em uma tabela
    #===========================================================================
    def conditionsToRequestContentFromTable(self, table):
        conditions = [
            (self.db.api_group_permissions.group_id == self.key.group_id),
            (self.db.api_group_permissions.table_name == table),
            (self.db.api_group_permissions.http_method == self.http_method),
            (self.db.api_group_permissions.all_columns == True)
        ]

        return reduce(lambda a, b: (a & b), conditions)

    def conditionsToRequestContentFromTableColumn(self, table, column):
        """


        :type table: str
        :type column: str
        :param table: Uma string referente a uma tabela
        :param column: Uma string referente a uma coluna
        :return:
        """
        conditions = [
            (self.db.api_group_permissions.column_name == column),
            (self.db.api_group_permissions.table_name == table),
            (self.db.api_group_permissions.group_id == self.key.group_id),
            (self.db.api_group_permissions.http_method == self.http_method)
        ]

        return reduce(lambda a, b: (a & b), conditions)

    def conditionsToRequestContentFromTableColumns(self, table, columns):
        """
        Condiçoes para requisitar conteúdo de uma lista de colunas.
        Quando uma lista de colunas é passada, a API deve verificar se o grupo da chave possui permissões para cara uma
        das colunas requisitadas ou se possui a permissao ALL_COLUMNS marcada para a tabela requisitada.

        :type table: str
        :type column: str
        :param table: Uma string referente a uma tabela
        :param column: Uma string referente a uma coluna
        """
        conditions = [
            reduce(lambda a, b: (a & b), [self.conditionsToRequestContentFromTableColumn(table, column) for column in columns]),
            self.conditionsToRequestAnyContentFromTable(table)
        ]

        return reduce(lambda a, b: (a | b), conditions)

    def conditionsToRequestAnyContentFromTable(self, table):
        """
        Condições para requisitar qualquer conteúdo (coluna) de uma tabela.
        Utilizado quando FIELDS não é especificado, visto que significa que foram requisitados todos os FIELDS de uma table.

        :type table: str
        :param table: Uma string referente a uma tabela
        """
        conditions = [
            (self.db.api_group_permissions.table_name == table),
            (self.db.api_group_permissions.group_id == self.key.group_id),
            (self.db.api_group_permissions.http_method == self.http_method),
            (self.db.api_group_permissions.all_columns == True)
        ]

        return reduce(lambda a, b: (a & b), conditions)