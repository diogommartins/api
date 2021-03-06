from definers.base import TableDefinerObserver
import abc
import json
import threading
import os


class ModelCreator(TableDefinerObserver):
    __metaclass__ = abc.ABCMeta

    def __init__(self, dir_path):
        self.dir_path = dir_path

        if not os.path.isdir(self.dir_path):
            os.mkdir(self.dir_path)

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
    Class responsible for parsing and serializing the list of
    tables and columns as JSON
    """

    def __init__(self, dir_path, file_name):
        super(JSONModelCreator, self).__init__(dir_path)
        self.file_path = os.path.join(self.dir_path, file_name)

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
        return {k: {field.name: field.type for field in v} for k, v in
                tables.iteritems()}


class Web2pyModelCreator(ModelCreator):
    model_file_name = 'definition.py'

    def __init__(self, dir_path, db_name="datasource"):
        super(Web2pyModelCreator, self).__init__(dir_path)
        self.db_name = db_name

    def _should_write(self):
        return True

    def _replace_quotes(self, a_str):
        return a_str.replace('"', "'")

    def __field_str(self, field):
        template = 'Field("{name}", "{type}", ' \
                   'length="{length}", label="{label}", notnull={notnull})'
        return template.format(name=field.name,
                               type=field.type,
                               length=field.length,
                               label=self._replace_quotes(field.label),
                               notnull=field.notnull)

    def __model_str(self, table, fields, pkey):
        """
        :type fields: list[Field]
        """
        return "{db_name}.define_table('{table}',\n{fields},\n" \
               "migrate=False,\nredefine=True,\nprimarykey={pkey})".format(
                db_name=self.db_name,
                table=table,
                fields=",\n".join(self.__field_str(field) for field in fields),
                pkey=pkey)

    def _writer(self, data):
        for table, model_str in data.iteritems():
            model_dir = self.dir_path + table
            if not os.path.isdir(model_dir):
                os.mkdir(model_dir)
            with open(os.path.join(model_dir, self.model_file_name), 'w') as fp:
                fp.write("# coding=utf-8\n")
                fp.write(model_str)

    def _parsed_data(self, data):
        tables, indexes = data
        return {table: self.__model_str(table, fields, indexes.get(table, []))
                for table, fields in tables.iteritems()}
