# -*- coding: utf-8 -*-
from gluon.html import *


class TableBeautify(object):
    excludedTables = ['COLUMNS']

    def __init__(self, db):
        """
        :param db: gluon.dal.DAL
        """
        self.db = db
        self.tables = {table: [] for table in self.db.tables}

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

    def _getFieldDescription(self, name, field):
        if self.db[name][field].label:
            return self.db[name][field].label
        return "Sem descrição"
