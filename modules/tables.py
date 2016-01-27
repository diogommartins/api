# -*- coding: utf-8 -*-
from gluon.html import *


class TableBeautify(object):
    excluded_tables = ['COLUMNS']

    def __init__(self, db):
        """
        :param db: gluon.dal.DAL
        """
        self.db = db

    def table(self, name):
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
            TBODY(*self.__format_table_rows(name)),
            _id='table_' + name,
            _class='tableDescriptions'
        )
        return table

    def __format_table_rows(self, name):
        """
        Para uma determinada tabela, retorna uma Lista de TR contendo duas colunas: "nome no campo" e "tipo de dado"

        :param name: O nome da tabela
        :return:
        """
        for field in self.db[name].fields:
            field_data_type = self.db[name][field].type
            yield TR(
                TD(field),
                TD(field_data_type, _class="row_type_" + field_data_type),
                TD(self.__get_field_description(name, field))
            )

    def __get_field_description(self, name, field):
        if self.db[name][field].label:
            return self.db[name][field].label
        return "Sem descrição"
