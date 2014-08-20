# -*- coding: utf-8 -*-
from gluon import current

class APIQuery():
    ENTRIES_PER_QUERY_DEFAULT = 10
    ENTRIES_PER_QUERY_MAX = 5000

    def __init__( self, tablename, fields, request_vars, return_fields=None ):
        self.table = current.dbSie[tablename]
        self.fields = fields['valid']
        self.special_fields = fields['special']
        self.request_vars = request_vars
        self.return_fields = (self._getReturnFields( return_fields )) if return_fields else []

    # Gera diferentes tipos de consultas para tipos de dados diferentes
    # Return: List
    def _getQueryStatement(self):
        conditions = []
        # Consultas normais
        for field in self.fields:
            if self.table[field].type == 'integer':
                conditions.append( self.table[field] == self.request_vars[field] )
            elif self.table[field].type == 'string':
                conditions.append( self.table[field].contains(self.request_vars[field], case_sensitive=False) )
            elif self.table[field].type == 'date':
                conditions.append( self.table[field] == self.request_vars[field] )

        # Trata condições especiais
        for special_field in self.special_fields:
            field = self.specialFieldChop( special_field )
            if self.table[field].type == 'date':
                if special_field.endswith('_MIN'):
                    conditions.append( self.table[field] > self.request_vars[special_field] )
                elif special_field.endswith('_MAX'):
                    conditions.append( self.table[field] < self.request_vars[special_field] )

        return conditions

    # Retirar essa funcao daqui e ver porque import de APIRequest nao ta funcionando
    def specialFieldChop(self, field):
        DEFAULT_SUFIX_SIZE = 4
        validSufixes = ('_MIN', '_MAX', '_BET')
        if field.endswith( validSufixes ):
            return field[:-DEFAULT_SUFIX_SIZE]
        return False

    # Return: List
    def _getReturnFields(self, return_fields):
        arr = []
        for field in return_fields:
            arr.append( self.table[field] )
        return arr

    # Retorna a tupla do limite
    # Return: Tuple
    def _getRecordsSubset(self):
        limits = {
                  "min" : 0,
                  "max" : self.ENTRIES_PER_QUERY_DEFAULT
                  }
        # Caso o usário passe os parâmetros LMIN e LMAX
        if set( ['LMIN', 'LMAX'] ).issubset( self.request_vars ):
            min = int( self.request_vars['LMIN'] )
            max = int( self.request_vars['LMAX'] )

            entriesToLimit = self.ENTRIES_PER_QUERY_MAX - max - min
            limits['max'] = max if (entriesToLimit > 0) else (max + entriesToLimit) # Se subset maior do que o estabelecido, corrige

        return ( limits['min'], limits['max'] )


    # Retorna as linhas com as colunas requisitadas
    # Return: Dict
    def execute(self):
        conditions = self._getQueryStatement()
        recordsSubset = self._getRecordsSubset()
        if conditions:
            count = current.dbSie( *conditions ).count()
            ret = current.dbSie( *conditions ).select( limitby=recordsSubset, *self.return_fields )
        else:
            count = current.dbSie( self.table ).count()
            ret = current.dbSie( self.table ).select( limitby=recordsSubset, *self.return_fields )

        if ret:
            return { "count" : count, "content" : ret, "subset" : recordsSubset }