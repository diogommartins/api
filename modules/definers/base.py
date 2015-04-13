# coding=utf-8
from gluon import current


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

        for table in field_collection:
            self.db.define_table(
                table,
                *field_collection[table],
                migrate=False,
                primarykey=_primarykey(table)
            )

    def _primarykey(self, table):
        raise NotImplementedError

    def _fetch_columns(self):
        raise NotImplementedError

    def _fetch_indexes(self):
        raise NotImplementedError

    def refresh_cache(self):
        raise NotImplementedError