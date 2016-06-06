# coding=utf-8=
from .base import BaseTableDefiner
from gluon.dal import Field
from unicodedata import normalize


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

    def _define_source_tables(self):
        self.db.define_table(
            'TABLES',
            Field('TABNAME'),
            Field('TABSCHEMA'),
            migrate=False,
            rname='SYSCAT.TABLES',
            primarykey=['TABNAME', 'TABSCHEMA']
        )

        self.db.define_table(
            'VIEWS',
            Field('VIEWNAME'),
            Field('VIEWSCHEMA'),
            migrate=False,
            rname='SYSCAT.VIEWS',
            primarykey=['VIEWNAME', 'VIEWSCHEMA']
        )

        self.db.define_table(
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

        self.db.define_table(
            'INDEXES',
            Field('TABSCHEMA'),
            Field('TABNAME'),
            Field('COLNAMES'),
            Field('UNIQUERULE'),
            migrate=False,
            rname='SYSCAT.INDEXES',
            primarykey=['TABSCHEMA', 'TABNAME']
        )

    def __colnames_parser(self, keys, separator='+'):
        """
        Chaves primárias são separadas por '+' -> Exemplo +ID_DOCUMENTO+ID_APLIC_ACAO
        """
        return [k.lower() for k in keys.split(separator)[1:]]

    def _fetch_indexes(self):
        rows = self.db((self.db.INDEXES.TABSCHEMA == self.schema) & (self.db.INDEXES.UNIQUERULE == 'P')).select(
            self.db.INDEXES.TABNAME,
            self.db.INDEXES.COLNAMES
        )
        return {table.TABNAME.lower(): self.__colnames_parser(table.COLNAMES) for table in rows}

    @property
    def _tables(self):
        """
        :rtype : dict
        """
        table_names = self.db(self.db.TABLES.TABSCHEMA == self.schema).select(self.db.TABLES.TABNAME)
        return {table.TABNAME.lower(): [] for table in table_names}

    def _fetch_columns(self):
        tables = self._tables.copy()
        cols = self.db(self.db.COLUMNS.TABSCHEMA == self.schema).select(
            self.db.COLUMNS.TABNAME,
            self.db.COLUMNS.COLNAME,
            self.db.COLUMNS.LENGTH,
            self.db.COLUMNS.TYPENAME,
            self.db.COLUMNS.REMARKS,
            self.db.COLUMNS.SCALE
        )

        def __type(col):
            if col.TYPENAME == 'DECIMAL':
                return "decimal(%i,%i)" % (col.LENGTH, col.SCALE)
            return self.types[col.TYPENAME]

        for col in cols:
            try:
                tables[col.TABNAME.lower()].append(Field(col.COLNAME.lower(), __type(col), length=col.LENGTH, label=col.REMARKS))
            except SyntaxError:
                try:
                    # Some colnames may have non-ascii characters, wich needs to be removed and passed as rname
                    normalized_name = normalize('NFKD', col.COLNAME.decode(self.db._db_codec)).encode('ASCII', 'ignore')
                    tables[col.TABNAME.lower()].append(Field(normalized_name.lower(), __type(col),
                                                             length=col.LENGTH, label=col.REMARKS, rname=col.COLNAME))
                except SyntaxError as e:
                    # É ascii e ainda sim é funny name. provavelemnte é palavra reservado no python e
                    # fere a regra REGEX_PYTHON_KEYWORDS
                    # todo: É a melhor abordagem? Estamos ignorando por enquanto
                    print e
            except KeyError:
                print "Não foi possível adicionar a coluna %s de %s - tipo %s desconhecido" % (col.COLNAME,
                                                                                               col.TABNAME,
                                                                                               col.TYPENAME)
        return tables
