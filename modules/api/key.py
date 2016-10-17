# -*- coding: utf-8 -*-
from datetime import datetime
from .cipher import AESCipher
from .request import Request
from gluon import current, HTTP


class Key(object):
    def __init__(self, db, hash=None):
        """
        :type db: gluon.DAL
        """
        self.db = db
        self.cache = (current.cache.ram, 86400)
        self.hash = hash
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.auth = self.auth_for_hash(hash)
        if self.auth:
            self.max_request, self.max_entries = self.request_limits()

    def owner(self):
        """
        Retorna o user_id do dono da API Key

        :rtype : int
        :return:
        """
        auth_key_owner = self.db(self.db.api_auth.auth_key == self.hash).select(self.db.api_auth.user_id).first()
        if auth_key_owner:
            return auth_key_owner.user_id

    @property
    def group_id(self):
        membership = self.db(self.db.auth_membership.user_id == self.auth.user_id).select().first()
        return membership.group_id

    def _make_hash(self, username):
        """
        Método utilizado para criar um novo hash a ser utilizado como API Key para o usuário

        :type username: str
        :rtype : str
        """
        aes = AESCipher()
        return aes.encrypt(username + self.timestamp)

    def genarate_new_key_for_user(self, user_id):
        """
        Gera uma nova chave valida para o usuário, inutiliza a anterior e retorna a nova chave criada.

        :rtype : str
        :param user_id:
        :return:
        """
        user = self.db(self.db.auth_user.id == user_id).select(self.db.auth_user.username).first()
        if user:
            new_key = self._make_hash(user.username)
            previous_key = self.db(
                    (self.db.api_auth.user_id == user_id) &
                    (self.db.api_auth.active == True)
            ).select().first()
            if previous_key:
                previous_key.update_record(active=False)
            self.db.api_auth.insert(
                    auth_key=new_key,
                    user_id=user_id,
                    dt_creation=self.timestamp,
                    active=True
            )
            self.db.commit()
            return new_key

    @staticmethod
    def get_current_active_key_for_user(user_id):
        """
        Dado um usuário válido cadastrado em um grupo, e com uma chave válida, o método retorna a chave ativa no momento

        :rtype : str
        :param user_id: O ID de um usuário na tabela auth_user
        :return: O hash de uma chave válida
        """
        db = current.db
        api_auth = db((db.api_auth.user_id == user_id) & (db.api_auth.active == True)).select().first()
        if api_auth:
            return api_auth.auth_key

    def auth_for_hash(self, hash):
        """
        Dado um determinado hash, o método retornará a entrada da tabela api_auth correspondente,
        caso seja um hash válido e a chave esteja ativa.

        :rtype : gluon.DAL.Row
        :return: Uma entrada da tabela api_auth
        """
        return self.db(
                (self.db.api_auth.auth_key == hash) & (self.db.api_auth.active == True)
        ).select(cache=self.cache, cacheable=True).first()

    def request_limits(self):
        """
        Dada uma chave, retorna uma tupla com o máximo de requisições diárias e o máximo de entradas que podem ser
        retornadas por vez.

        :rtype : tuple
        """
        limits = self.db(
                (self.db.auth_membership.user_id == self.auth.user_id) & (
                self.db.auth_membership.group_id == self.db.api_request_type.group_id)
        ).select(self.db.api_request_type.max_requests,
                 self.db.api_request_type.max_entries,
                 cache=self.cache, cacheable=True).first()

        return limits.max_requests, limits.max_entries


class KeyPermissions(object):
    cache = (current.cache.ram, 86400)

    def __init__(self):
        """
        TODO: modificar atributos hash e key para receber um objeto do tipo APIKey
        :type self: object
        :param request: Uma requisição HTTP
        """
        self.db = current.db
        self.datasource = current.datasource

    @staticmethod
    def http_method_with_name(method):
        """
        Dado um determinado método, retorna o seu ID, caso o mesmo seja suportado pela API

        :param method: Uma string correspondente a um método HTTP
        :return: O id de um método
        :raise HTTP: 405 caso o método requisitado não seja suportado pela API
        """
        db = current.db
        valid_method = db(db.api_methods.http_method == method).select(db.api_methods.id,
                                                                       cache=KeyPermissions.cache).first()
        if valid_method:
            return valid_method.id
        else:
            raise HTTP(405, "Método requisitado não é suportado.")


class EndpointPermissions(KeyPermissions):
    def __init__(self, endpoint, key, method, fields):
        """
        :type endpoint: str
        :type key: Key
        :type method: str
        :type fields: list
        """
        super(EndpointPermissions, self).__init__()
        self.endpoint = endpoint
        self.fields = fields
        self.http_method = KeyPermissions.http_method_with_name(method)
        self.hash = key.hash
        self.key = self.db(self.db.v_api_calls.auth_key == self.hash).select(cache=self.cache, cacheable=True).first()

    def can_perform_api_call(self):
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
        if not self.key.active:
            raise HTTP(403, "Chave inativa")
        if not self.key.total_requests < self.key.max_requests:
            raise HTTP(429, "Número máximo de requisições esgotado.")
        if not self._has_permission_to_request_fields():
            raise HTTP(403, "APIKey não possui permissão para acessar o recurso requisitado.")

        return True

    def _has_permission_to_request_fields(self):
        """
        Caso FIELDS tenham sido especificados, verificará se existe alguma proibição
        de acesso a dados na tabela ou nas colunas requisitadas

        Caso FIELDS não tenha sido especificado, considera-se que a requisição deseja
        acessar a todo o conteúdo da tabela. Então, verifica-se se existe restrição em
        pelo menos uma das coluna da tabela

        * As consultas de permissão são cacheadas em 3600 segundos

        :rtype : bool
        :return:
        """
        if len(self.fields) > 0:
            valid_fields = self._validate_return_fields(self.fields)
            has_permission = self.db(
                    self.__can_request_columns_from_table(self.endpoint, valid_fields)).select(
                    self.db.api_group_permissions.id, cache=self.cache)
            if has_permission:
                return True
        else:
            has_permission = self.db(self.__can_request_any_column_from_table(self.endpoint)).select(
                    self.db.api_group_permissions.id, cache=self.cache)
            if has_permission:
                return True
        return False

    def _validate_return_fields(self, fields):
        """
        Método para verificar se os parâmetros de retorno passados são válidos

        :type fields: list
        :param fields: Lista de fields requisitados
        :return: Retorna uma lista com os FIELDS válidos ou uma lista vazia, que é interpretada como todas as colunas
        """
        return [field for field in fields if field in self.datasource[self.endpoint].fields]

    def __can_request_column_from_table(self, table, column):
        """
        :type table: str
        :type column: str
        :param table: Uma string referente a uma tabela
        :param column: Uma string referente a uma coluna
        :return:
        """
        conditions = (
            (self.db.api_group_permissions.column_name.lower() == column),
            (self.db.api_group_permissions.table_name.lower() == table),
            (self.db.api_group_permissions.group_id == self.key.group_id),
            (self.db.api_group_permissions.http_method == self.http_method)
        )

        return reduce(lambda a, b: (a & b), conditions)

    def __can_request_columns_from_table(self, table, columns):
        """
        Condiçoes para requisitar conteúdo de uma lista de colunas.
        Quando uma lista de colunas é passada, a API deve verificar se o grupo da chave possui permissões para cara uma
        das colunas requisitadas ou se possui a permissao ALL_COLUMNS marcada para a tabela requisitada.

        :type table: str
        :type columns: list
        :param table: Uma string referente a uma tabela
        :param columns: Uma lista referente a uma colunas da tabela `table`
        """
        conditions = (
            reduce(lambda a, b: (a & b),
                   [self.__can_request_column_from_table(table, column) for column in columns]),
            self.__can_request_any_column_from_table(table)
        )

        return reduce(lambda a, b: (a | b), conditions)

    def __can_request_any_column_from_table(self, table):
        """
        Condições para requisitar qualquer conteúdo (coluna) de uma tabela.
        Utilizado quando FIELDS não é especificado, visto que significa que foram requisitados todos os FIELDS de uma table.

        :type table: str
        :param table: Uma string referente a uma tabela
        """
        conditions = (
            (self.db.api_group_permissions.table_name.lower() == table),
            (self.db.api_group_permissions.group_id == self.key.group_id),
            (self.db.api_group_permissions.http_method == self.http_method),
            (self.db.api_group_permissions.all_columns == True)
        )

        return reduce(lambda a, b: (a & b), conditions)


class ProcedurePermissions(KeyPermissions):
    def __init__(self, api_key, procedure_name):
        super(ProcedurePermissions, self).__init__()
        self.api_key = api_key
        self.procedure_name = procedure_name

    def can_perform_api_call(self):
        table = self.db.api_procedure_permissions
        condition = self.db((table.name == self.procedure_name) &
                            (table.group_id == self.api_key.group_id)).select(cache=self.cache, cacheable=True).first()
        return condition
