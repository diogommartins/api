# -*- coding: utf-8 -*-
from gluon.html import *


class TableBeautify(object):
    excludedTables = ['COLUMNS']

    def __init__(self, db, descriptions):
        self.db = db
        self.descriptions = self._formatTableColumnsDescriptions(descriptions)

    def beautifyDatabaseTables(self):
        return [self.printTable(tableName) for tableName in self.db.tables if tableName not in self.excludedTables]

    def printTable(self, name):
        """
        Retorna uma tabela HTML correspondente a estrutura de um endpoint
        :param name:
        :rtype: gluon.html.TABLE
        """
        table = TABLE(
            THEAD(
                TR(TH(name, _colspan=3)),
                TR(TH('Field'), TH('Type'), TH('Description'))
            ),
            TBODY(*self._formatTableRows(name)),
            _id='table_' + name,
            _class='tableDescriptions'
        )
        return table

    def _formatTableRows(self, name):
        """
        Para uma determinada tabela, retorna uma Lista de TR contendo duas colunas: "nome no campo" e "tipo de dado"

        :param name: O nome da tabela
        :return:
        """
        for field in self.db[name].fields:
            fieldDataType = self.db[name][field].type
            yield TR(
                TD(field),
                TD(fieldDataType, _class="row_type_" + fieldDataType),
                TD(self._getFieldDescription(name, field))
            )

    def _formatTableColumnsDescriptions(self, descriptions):
        tableColumnsDescriptions = {}
        for row in descriptions:
            if row.TABNAME in tableColumnsDescriptions:
                tableColumnsDescriptions[row.TABNAME].update({row.COLNAME: row.REMARKS})
            else:
                tableColumnsDescriptions.update({row.TABNAME: {row.COLNAME: row.REMARKS}})

        return tableColumnsDescriptions

    def _getFieldDescription(self, name, field):
        if name in self.descriptions and field in self.descriptions[name]:
            return self.descriptions[name][field]
        return "Sem descrição"
