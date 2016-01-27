from definers.base import TableDefinerObserver
import json
import threading
import os


class JSONModelCreator(TableDefinerObserver):
    """
    Class responsible for parsing and serializing the list of tables and columns as JSON
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def __should_write(self):
        """
        Returns whether or not to write the output file.
        :rtype: bool
        """
        return not os.path.isfile(self.file_path)

    def __writer(self, data):
        with open(self.file_path, 'w') as fp:
            json.dump(data, fp, indent=4)
            print('Model file created at "{path}".'.format(path=self.file_path))

    def __parse_data(self, data):
        return {k: {field.name: field.type for field in v} for k, v in data.iteritems()}

    def source_tables_did_load(self, tables):
        if self.__should_write():
            work = threading.Thread(name=self.__class__.__name__,
                                    target=self.__writer,
                                    args=(self.__parse_data(tables),))
            work.start()
