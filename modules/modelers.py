from definers.base import TableDefinerObserver
import abc
import json
import threading
import os


class ModelCreator(TableDefinerObserver):
    __metaclass__ = abc.ABCMeta

    def __init__(self, file_path):
        self.file_path = file_path

    @abc.abstractmethod
    def _should_write(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _parsed_data(self, data):
        raise NotImplementedError

    @abc.abstractmethod
    def _writer(self, data):
        raise NotImplementedError

    def source_tables_did_load(self, metadata):
        if self._should_write():
            work = threading.Thread(name=self.__class__.__name__,
                                    target=self._writer,
                                    args=(self._parsed_data(metadata),))
            work.start()


class JSONModelCreator(ModelCreator):
    """
    Class responsible for parsing and serializing the list of tables and columns as JSON
    """
    def _should_write(self):
        """
        Returns whether or not to write the output file.
        :rtype: bool
        """
        return not os.path.isfile(self.file_path)

    def _writer(self, data):
        with open(self.file_path, 'w') as fp:
            json.dump(data, fp, indent=4)
            print('Model file created at "{path}".'.format(path=self.file_path))

    def _parsed_data(self, data):
        tables, indexes = data
        return {k: {field.name: field.type for field in v} for k, v in tables.iteritems()}


class Web2pyModelCreator(ModelCreator):
    model_file_name = 'definition.py'

    def __init__(self, file_path, db_name="datasource"):
        super(Web2pyModelCreator, self).__init__(file_path)
        self.db_name = db_name

    def _should_write(self):
        return True

    def __model_str(self, table, fields, pkey):
        """
        :type fields: list[Field]
        """
        return "{db_name}.define_table('{table}',\n{fields},\nmigrate=False,\nredefine=True,\nprimarykey={pkey})".format(
            db_name=self.db_name,
            table=table,
            fields=",\n".join(["Field('{name}', '{type}')".format(name=f.name, type=f.type) for f in fields]),
            pkey=pkey
        )

    def _writer(self, data):
        for table, model_str in data.iteritems():
            model_dir = self.file_path + table
            if not os.path.isdir(model_dir):
                os.mkdir(model_dir)
            with open(os.path.join(model_dir, self.model_file_name), 'w') as fp:
                fp.write(model_str)

    def _parsed_data(self, data):
        tables, indexes = data
        return {table: self.__model_str(table, fields, indexes.get(table, [])) for table, fields in tables.iteritems()}
