# -*- coding: utf-8 -*-
from gluon import current
from gluon.html import *
class TableBeautify():
    def __init__(self, tables):
        self.tables = tables
        self.dbSie = current.dbSie

    def beautifyDatabaseTables(self):
        tables = []
        for tableName in self.tables:
            tables.append( self.printTable(tableName) )
        return tables

    # Para uma determinada tabela, returna um TABLE Helper
    def printTable(self, tableName):
        table = TABLE(
                      THEAD(TR(TH(tableName), _colspan=2, _class='tableName'),
                            TR(TH('Field'), TH('Type'), TH('Description'))
                            ),
                      self._formatTableRows(tableName),
                      _id='table_' + tableName
                      )
        return table

    # Para uma determinada tabela, retorna uma Lista de TR contendo duas colunas: "nome no campo" e "tipo de dado"
    def _formatTableRows(self, tableName):
        rows = []
        for field in self.dbSie[tableName].fields:
            fieldDataType = self.dbSie[tableName][field].type
            rows.append( TR( TD(field),TD(fieldDataType),TD('A ser implementado.'), _class="row_type_" + fieldDataType) )
        return rows