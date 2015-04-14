# coding=utf-8
from gluon import current
from gluon.dal import Field


class BaseTableDefiner(object):
    types = {}

    def __init__(self, datasource, schema, cache_model=current.cache.ram, cache_time=86400, verbose=False):
        """
        :type datasource: gluon.dal.base.DAL
        :type schema: str
        :type cache_time: int
        :type verbose: bool
        """
        self.db = datasource
        self.schema = schema
        self.cache = cache_model
        self.cache_time = cache_time
        self.verbose = verbose
        self.tables = lambda: self.cache(self.db._uri_hash, lambda: self._fetch_columns(), time_expire=self.cache_time)
        self.indexes = lambda: self.cache(self.db._uri_hash + 'indexes', lambda: self._fetch_indexes(), time_expire=self.cache_time)
        self._define_source_tables()
        self._define_tables()

    def _define_source_tables(self):
        raise NotImplementedError

    def _define_tables(self):
        field_collection = self.tables()
        indexes = self.indexes()

        def _primarykey(table):
            """
            :rtype : list
            """
            try:
                return indexes[table]
            except KeyError:
                if self.verbose:
                    print "[ALERT] Tabela %s não possui chave primária e alguns recursos podem não funcionar" % table
                return []

        for table in field_collection:
            self.db.define_table(
                table,
                *field_collection[table],
                migrate=False,
                primarykey=_primarykey(table)
            )

    def _fetch_columns(self):
        """
        Method that returns a dictionary which keys are table names and values are lists of gluon.Field equivalents to
        table columns

        :rtype : dict
        """
        raise NotImplementedError

    def _fetch_indexes(self):
        """
        Method that returns a dictionary which keys are table names and values are lists of primary keys
        :rtype : dict
        """
        raise NotImplementedError

    def refresh_cache(self):
        raise NotImplementedError


class InformationSchema(BaseTableDefiner):
    def _define_source_tables(self):
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
            Field('constraint_schema'),
            Field('constraint_name'),
            Field('table_catalog'),
            Field('table_name'),
            Field('table_schema'),
            migrate=False,
            rname='information_schema.key_column_usage'
        )

    @property
    def _tables(self):
        """
        :rtype : dict
        """
        table_names = self.db(self.db.columns.table_schema == self.schema).select(self.db.columns.table_name,
                                                                                  distinct=True)
        return {table.table_name: [] for table in table_names}

    def _fetch_columns(self):
        tables = self._tables.copy()
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
        indexes = self._tables.copy()

        rows = self.db((self.db.table_constraints.table_schema == self.schema) &
                       (self.db.table_constraints.table_name == self.db.key_column_usage.table_name) &
                       (self.db.table_constraints.constraint_name == self.db.key_column_usage.constraint_name) &
                       (self.db.table_constraints.constraint_type == 'PRIMARY KEY')).select(
            self.db.table_constraints.table_name, self.db.key_column_usage.column_name)

        for index in rows:
            indexes[index.table_constraints.table_name].append(index.key_column_usage.column_name)

        return indexes

    def refresh_cache(self):
        #TODO Escrever método para dar refresh na lista de tabelas para atualizar alterações feitas na estrutura sem que seja necessário reiniciar o webserver
        raise NotImplementedError