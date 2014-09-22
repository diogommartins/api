# -*- coding: utf-8 -*-
from gluon import current
from gluon.html import *
class TableBeautify():
    excludedTables = ['COLUMNS']

    def __init__(self, tables, descriptions):
        self.tables = tables
        self.dbSie = current.dbSie
        self.descriptions = self._formatTableColumnsDescriptions(descriptions)

    def beautifyDatabaseTables(self):
        tables = []
        for tableName in self.tables:
            if tableName not in self.excludedTables:
                tables.append( self.printTable(tableName) )
        return tables

    # Para uma determinada tabela, returna um TABLE Helper
    def printTable(self, tableName):
        table = TABLE(
                      THEAD( TR(TH(tableName,_colspan=3)) ),
                      THEAD( TR(TH('Field'), TH('Type'), TH('Description') ) ),
                      TBODY( self._formatTableRows(tableName) ),
                      _id='table_' + tableName,
                      _class='tableDescriptions'
                      )
        return table

    # Para uma determinada tabela, retorna uma Lista de TR contendo duas colunas: "nome no campo" e "tipo de dado"
    def _formatTableRows(self, tableName):
        rows = []
        for field in self.dbSie[tableName].fields:
            fieldDataType = self.dbSie[tableName][field].type
            rows.append( TR( TD(field),
                             TD(fieldDataType, _class="row_type_" + fieldDataType),
                             TD( self._getFieldDescription(tableName, field) )) )
        return rows

    #===========================================================================
    #
    #===========================================================================
    def _formatTableColumnsDescriptions(self, descriptions):
        tableColumnsDescriptions = {}
        for row in descriptions:
            if row.TABNAME in tableColumnsDescriptions:
                tableColumnsDescriptions[row.TABNAME].update( {row.COLNAME : row.REMARKS} )
            else:
                tableColumnsDescriptions.update( {row.TABNAME : { row.COLNAME : row.REMARKS }} )

        return tableColumnsDescriptions

    def _getFieldDescription(self, tableName, field):
        if tableName in self.descriptions:
            if field in self.descriptions[tableName]:
                return self.descriptions[tableName][field]
        return "Sem descrição"
