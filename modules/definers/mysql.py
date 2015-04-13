from .base import BaseTableDefiner


class MySQLTableDefiner(BaseTableDefiner):
    def __init__(self, datasource, schema, **kwargs):
        super(MySQLTableDefiner, self).__init__(datasource, schema, **kwargs)