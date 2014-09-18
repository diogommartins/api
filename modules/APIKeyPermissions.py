# -*- coding: utf-8 -*-
from gluon import current

class APIKeyPermissions():
    def __init__( self, hash ):
        self.hash = hash
        self.db = current.db
        ret = self.db( self.db.v_api_calls.auth_key == hash ).select().first()

        if ret:
            self.dt_creation = ret.dt_creation
            self.active = ret.active
            self.user_id = ret.user_id
            self.group_role = ret.group_role
            self.group_id = ret.group_id
            self.max_requests = ret.max_requests
            self.max_entries = ret.max_entries
            self.total_requests = ret.total_requests

    # Se chave estiver ativa e a quantidade de requisições aidna não estrapolou o limite diário
    # Return: Boolean
    def canPerformAPICall(self):
        if self.active:
            if (self.total_requests < self.max_requests):
                return True
            else:
                raise Exception( "Número máximo de requisições esgotado." )
        else:
            raise Exception( "Chave inativa" )

    #===========================================================================
    # Condição para
    #===========================================================================
    def conditionsToRequestContentFromTable(self, table):
        conditions = [ (self.db.api_group_restrictions.role_group == self.group_id),
                       (self.db.api_group_restrictions.table == table),
                       (self.db.api_group_restrictions.all != True) ]
        return conditions

    #===========================================================================
    #
    #===========================================================================
    def conditionsToRequestContentFromTableColumns(self, table, columns):
        return [ ( (self.db.api_group_restrictions.column == column)
                   &(self.db.api_group_restrictions.role_group == self.group_id)
                   &(self.db.api_group_restrictions.table==table)
                   ) for column in columns ]

