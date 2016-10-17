# coding=utf-8
import abc

from abstracts import Observable
from gluon import current, HTTP
from gluon.dal import Field
import threading


class DefinerThreadWorker():
    TABLES_PER_THREAD = 500

    def __init__(self, job, tables):
        """
        This class is responsible for dividing the table definition workload equally between threads

        :type job: callable
        :type tables: list
        """
        self.job = job
        self.tables = tables
        self.chunks = self.__chunks(self.tables, self.TABLES_PER_THREAD)
        self.threads = tuple(self.__create_thread(tables) for tables in self.chunks)

    def __chunks(self, l, n):
        """
        Yield successive n-sized chunks from l.
        """
        for i in xrange(0, len(l), n):
            yield l[i:i+n]

    def __create_thread(self, tables):
        """
        Spawns a new thread, responsible for defining the `tables`

        :param tables: A list of tables
        :return: A new Thread object
        :rtype : threading.Thread
        """
        return threading.Thread(target=self.job, args=(tables,))

    def start(self):
        """
        Starts all threads activities
        """
        for thread in self.threads:
            thread.start()

    def join(self):
        """
        Wait for all threads to terminate before leaving.
        """
        for thread in self.threads:
            thread.join()


class BaseTableDefiner(Observable):
    types = {}

    def __init__(self, datasource, schema, cache_model=current.cache.ram, cache_time=86400, blacklist=None):
        """
        This is an abstract class used as a base for table model definer classes.
        The default object initialization would result in defining all endpoints for the selected `schema`
        and `datasource`, while initializing with `lazy_tables` as a list of valid endpoints names would
        define only those.
        If many tables need to be defined, a `DefinerThreadWorker` object is created to deal with the definition using
        multiple threads

        :type datasource: gluon.dal.base.DAL
        :type schema: str
        :type cache_time: int
        """
        self.db = datasource
        self.schema = schema
        self.cache = cache_model
        self.cache_time = cache_time
        self.blacklist = blacklist or tuple()
        self.tables = lambda: self.cache(self.db._uri_hash,
                                         lambda: self._fetch_columns(),
                                         time_expire=self.cache_time)
        self.indexes = lambda: self.cache(self.db._uri_hash + 'indexes',
                                          lambda: self._fetch_indexes(),
                                          time_expire=self.cache_time)
        self._define_source_tables()

    def not_in_blacklist_condition(self, field):
        conditions = reduce(lambda a, b: (a & b), (~field.lower().startswith(prefix.lower()) for prefix in self.blacklist))
        return conditions

    def _define_source_tables(self):
        """
        Method used to define the necessary tables to retrieve metadata of the existing tables on `datasource`
        """
        raise NotImplementedError

    def define_tables(self):
        """
        Basically, this method will call DAL.define_table of the given datasource, for each of the tables at self.tables
        Also, a 'source_tables_did_load' notification is published to registered observers.
        """
        field_collection = self.tables()

        indexes = self.indexes()

        self.notify_obervers('source_tables_did_load', TableDefinerObserver, (field_collection, indexes))

        def _define(tables):
            for table in tables:
                """
                A primary key must be a list. If None is passed into `primarykey` parameter of the `define_table` method,
                it will automatically define an `Id` field as a primary key.
                """
                try:
                    pkey = indexes[table]
                except KeyError:
                    pkey = []
                try:
                    self.db.define_table(table, *field_collection[table], migrate=False, primarykey=pkey, redefine=True)
                except KeyError:
                    raise HTTP(404, "Recurso requisitado é inválido: %s" % table)

        tables = field_collection.keys()

        if len(tables) < DefinerThreadWorker.TABLES_PER_THREAD:
            _define(tables)
        else:
            worker = DefinerThreadWorker(_define, tables)

            worker.start()
            worker.join()

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
        self.cache(self.db._uri_hash, None)
        self.cache(self.db._uri_hash + 'indexes', None)


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
        constraints = self.db.table_constraints

        usage = self.db.key_column_usage
        rows = self.db((constraints.table_schema == self.schema) &
                       (constraints.table_name == usage.table_name) &
                       (constraints.constraint_name == usage.constraint_name) &
                       (constraints.constraint_type == 'PRIMARY KEY')).select(
            constraints.table_name, usage.column_name)

        for index in rows:
            indexes[index.table_constraints.table_name].append(index.key_column_usage.column_name)

        return indexes


class TableDefinerObserver(object):
    """
    Class that defines observable actions from the TableDefiners
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def source_tables_did_load(self, metadata):
        raise NotImplementedError
