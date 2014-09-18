# -*- coding: utf-8 -*-
from gluon import current

class APIKeyPermissions():
    def __init__( self, request ):
        self.request = request
        self.hash = self.request.vars.API_KEY
        self.db = current.db
        #=======================================================================
        # key pode ser nula ou ter as propriedades:
        #
        # dt_creation, active, user_id, group_role, group_id, max_requests, max_entries
        # total_requests
        #=======================================================================
        self.key = self.db( self.db.v_api_calls.auth_key == self.hash ).select().first()

    # Se chave estiver ativa e a quantidade de requisições aidna não estrapolou o limite diário
    # Return: Boolean
    def canPerformAPICall(self):
        if self.key.active:
            if (self.key.total_requests < self.key.max_requests):
                if self._hasPermissionToRequestFields():
                    return True
                else:
                    raise Exception( "APIKey não possui permissão para acessar o recurso requisitado." )
            else:
                raise Exception( "Número máximo de requisições esgotado." )
        else:
            raise Exception( "Chave inativa" )

    #===========================================================================
    # Caso FIELDS tenham sido especificados, verificará os pedidos, caso nao,
    # verifica-se a permissão para ALL
    #
    #
    #
    # TODO : DOCUMENTAAAAAAARRRRRRRRR
    #
    #
    #
    #===========================================================================
    def _hasPermissionToRequestFields(self):
        requestedFields = self.request.vars["FIELDS"].split(",") if self.request.vars["FIELDS"] else []
        if len( requestedFields ) > 0:
            validFields = self._validateReturnFields( requestedFields )
            dontHavePermission = self.db( self.conditionsToForbidRequestContentFromTableOrColumns(self.request.controller, validFields) ).select( self.db.api_group_restrictions.id )
            if dontHavePermission:
                return False
        else:
            dontHavePermission = self.db( self.conditionsToRequestAnyContentFromTable(self.request.controller) ).select( self.db.api_group_restrictions.id )
            if dontHavePermission:
                return False
        return True


    #===========================================================================
    # Método para verificar se os parâmetros de retorno passados são válidos
    #
    # Retorna uma lista com os FIELDS válidos ou uma lista vazia, que é interpretada
    # como todas as colunas
    # MÉTODO TAMBÉM EXISTEM EM APIRequest <<<<<< RESOLVER
    #===========================================================================
    def _validateReturnFields(self, fields):
        return[ field for field in fields if field in current.dbSie[self.request.controller].fields ]

    def conditionsToForbidRequestContentFromTableOrColumns(self, table, columns):
        return ( self.conditionsToForbidRequestContentFromTable(table)
                 |self.conditionsToRequestContentFromTableColumns(table, columns) )

    #===========================================================================
    # Condição para proibição total em uma tabela
    #===========================================================================
    def conditionsToForbidRequestContentFromTable(self, table):
        conditions = [ (self.db.api_group_restrictions.group_id == self.key.group_id),
                       (self.db.api_group_restrictions.table_name == table),
                       (self.db.api_group_restrictions.all_columns == True) ]

        return reduce(lambda a,b:(a&b), conditions )

    #===========================================================================
    # Condição para proibição em uma lista de colunas
    #===========================================================================
    def conditionsToRequestContentFromTableColumns(self, table, columns):
        conditions = [ ( (self.db.api_group_restrictions.column_name == column)
                         &(self.db.api_group_restrictions.group_id == self.key.group_id)
                         &(self.db.api_group_restrictions.table_name==table)
                         ) for column in columns ]

        return reduce(lambda a,b:(a|b), conditions )

    #===========================================================================
    # Condição para proibição de acesso a pelo menos uma coluna de uma tabela
    #===========================================================================
    def conditionsToRequestAnyContentFromTable(self, table):
        conditions = [ (self.db.api_group_restrictions.table_name==table),
                       (self.db.api_group_restrictions.group_id == self.key.group_id) ]

        return reduce(lambda a,b:(a&b), conditions )
