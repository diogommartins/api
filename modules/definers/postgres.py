# coding=utf-8
from .base import BaseTableDefiner
from gluon.dal import Field


class PostgreSQLTableDefiner(BaseTableDefiner):
    types = {
        'bigint': 'bigint',
        'bytea': 'blob',
        'character varying': 'string',
        'character': 'boolean',
        'date': 'date',
        'float': 'float',
        'float8': 'double',
        'integer': 'integer',
        'text': 'text',
        'time': 'time',
        'timestamp': 'datetime',
        'timestamp with timezone': 'datetime',
        'timestamp without time zone': 'datetime',
        'varchar': 'string'
    }

    def __init__(self, datasource, schema, **kwargs):
        super(PostgreSQLTableDefiner, self).__init__(datasource, schema, **kwargs)
        self.__define_source_tables()
        self._define_tables()

    def __define_source_tables(self):
        self.db.define_table(
            'columns',
            Field('table_catalog'),
            Field('table_name'),
            Field('table_schema'),
            Field('column_name'),
            Field('ordinal_position', 'integer'),
            Field('is_nullable'),
            Field('data_type'),
            Field('character_maximum_length', 'integer'),
            Field('numeric_precision', 'integer'),
            migrate=False,
            rname='information_schema.columns',
            primarykey=['table_catalog', 'table_schema', 'table_name', 'column_name']
        )

        self.db.define_table(
            'views',
            Field('table_catalog'),
            Field('table_schema'),
            Field('table_name'),
            migrate=False,
            rname='information_schema.views',
            primarykey=['table_catalog', 'table_schema', 'table_name']
        )

        self.db.define_table(
            'table_constraints',
            Field('constraint_schema'),
            Field('constraint_name'),
            Field('table_schema'),
            Field('table_name'),
            Field('constraint_type'),
            migrate=False,
            rname='information_schema.table_constraints',
            primarykey=['table_schema', 'table_name']
        )

        self.db.define_table(
            'key_column_usage',
            Field('column_name'),
            Field('table_catalog'),
            Field('table_name'),
            Field('table_schema'),
            migrate=False,
            rname='information_schema.key_column_usage'
        )

    @property
    def __tables(self):
        """
        :rtype : dict
        """
        table_names = self.db(self.db.columns.table_schema == self.schema).select(self.db.columns.table_name,
                                                                                  distinct=True)
        return {table.table_name: [] for table in table_names}

    def parse_boolean(self, value):
        return True if value == 'YES' else False

    def _fetch_columns(self):
        tables = self.__tables.copy()
        cols = self.db(self.db.columns.table_schema == self.schema).select(
            self.db.columns.table_name,
            self.db.columns.column_name,
            self.db.columns.data_type,
            self.db.columns.character_maximum_length,
            self.db.columns.is_nullable
        )

        def notnull(c):
            return False if c == 'YES' else True

        for col in cols:
            try:
                tables[col.table_name].append(
                    Field(col.column_name, self.types[col.data_type],
                          length=col.character_maximum_length,
                          notnull=notnull(col.is_nullable)))
            except KeyError:
                print "Não foi possível adicionar a coluna %s de %s - tipo %s desconhecido" % (
                    col.column_name, col.table_name, col.data_type)

        return tables

    def _fetch_indexes(self):
        indexes = self.__tables.copy()

        rows = self.db((self.db.table_constraints.table_schema == self.schema) &
                       (self.db.table_constraints.table_name == self.db.key_column_usage.table_name) &
                       (self.db.table_constraints.constraint_type == 'PRIMARY KEY')).select(
            self.db.table_constraints.table_name, self.db.key_column_usage.column_name)

        for index in rows:
            indexes[index.table_constraints.table_name].append(index.key_column_usage.column_name)

        return indexes

    def refresh_cache(self):
        #TODO Escrever método para dar refresh na lista de tabelas para atualizar alterações feitas na estrutura sem que seja necessário reiniciar o webserver
        raise NotImplementedError
