# coding=utf-8
from .base import BaseTableDefiner
from gluon import current

datasource.define_table(
    'TABLES',
    Field('TABNAME'),
    Field('TABSCHEMA'),
    migrate=False,
    rname='SYSCAT.TABLES',
    primarykey=['TABNAME', 'TABSCHEMA']
)

datasource.define_table(
    'VIEWS',
    Field('VIEWNAME'),
    Field('VIEWSCHEMA'),
    migrate=False,
    rname='SYSCAT.VIEWS',
    primarykey=['VIEWNAME', 'VIEWSCHEMA']
)

datasource.define_table(
    'COLUMNS',
    Field('TABNAME'),
    Field('TABSCHEMA'),
    Field('COLNAME'),
    Field('COLNO'),
    Field('LENGTH', 'integer'),
    Field('NULLS'),
    Field('SCALE'),
    Field('TYPENAME'),
    Field('REMARKS'),
    migrate=False,
    rname='SYSCAT.COLUMNS',
    primarykey=['TABSCHEMA', 'TABNAME', 'COLNAME']
)

datasource.define_table(
    'INDEXES',
    Field('TABSCHEMA'),
    Field('TABNAME'),
    Field('COLNAMES'),
    Field('UNIQUERULE'),
    migrate=False,
    rname='SYSCAT.INDEXES',
    primarykey=['TABSCHEMA', 'TABNAME']
)


class DB2TableDefiner(BaseTableDefiner):
    types = {
        'BIGINT': 'bigint',
        'BLOB': 'blob',
        'CHARACTER': 'string',
        'CLOB': 'text',
        'DATE': 'date',
        'DECIMAL': 'decimal',
        'DOUBLE': 'double',
        'INTEGER': 'integer',
        'LONG VARCHAR': 'text',
        'SMALLINT': 'integer',
        'TIME': 'time',
        'TIMESTAMP': 'datetime',
        'VARCHAR': 'string'
    }

    def __init__(self, datasource, schema, cache_model=current.cache.ram, cacheTime=86400, verbose=False):
        super(DB2TableDefiner, self).__init__(datasource, schema, cache_model, cacheTime, verbose)
        self.tables = self.cache(self.db._uri_hash, lambda: self.__columns, time_expire=self.cacheTime)
        self.indexes = self.cache(self.db._uri_hash + 'indexes', lambda: self.__indexes, time_expire=self.cacheTime)

    @property
    def __indexes(self):
        """
        Method that returns a dictionary which keys are table names and values are lists of primary keys
        :rtype : dict
        """
        rows = self.db((self.db.INDEXES.TABSCHEMA == self.schema) & (self.db.INDEXES.UNIQUERULE == 'P')).select(
            self.db.INDEXES.TABNAME,
            self.db.INDEXES.COLNAMES
        )
        return {table.TABNAME: table.COLNAMES.split('+')[1:] for table in rows}

    @property
    def __tables(self):
        """
        :rtype : tuple
        """
        table_names = self.db(self.db.TABLES.TABSCHEMA == self.schema).select(self.db.TABLES.TABNAME)
        return tuple(table.TABNAME for table in table_names)

    @property
    def __columns(self):
        """
        Method that returns a dictionary which keys are table names and values are lists of gluon.Field equivalents to
        table columns

        :rtype : dict
        """
        tables = {table: [] for table in self.__tables}
        cols = self.db(self.db.COLUMNS.TABSCHEMA == self.schema).select(
            self.db.COLUMNS.TABNAME,
            self.db.COLUMNS.COLNAME,
            self.db.COLUMNS.LENGTH,
            self.db.COLUMNS.TYPENAME,
            self.db.COLUMNS.REMARKS
        )
        for col in cols:
            try:
                tables[col.TABNAME].append(Field(col.COLNAME, self.types[col.TYPENAME], length=col.LENGTH, label=col.REMARKS))
            except KeyError:
                print "Não foi possível adicionar a coluna %s de %s - tipo %s desconhecido" % (
                    col.COLNAME, col.TABNAME, col.TYPENAME)

        return tables

    def __primarykey(self, table):
        """
        :rtype : list
        """
        try:
            return self.indexes[table]
        except KeyError:
            if self.verbose:
                print "[ALERT] Tabela %s não possui chave primária e alguns recursos podem não funcionar" % table

    def define_tables(self):
        for table in self.tables:
            self.db.define_table(
                table,
                *self.tables[table],
                migrate=False,
                primarykey=self.__primarykey(table)
            )

    def refresh_cache(self):
        #TODO Escrever método para dar refresh na lista de tabelas para atualizar alterações feitas na estrutura sem que seja necessário reiniciar o webserver
        raise NotImplementedError