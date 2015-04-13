# coding=utf-8
from .base import BaseTableDefiner


class MSSQLTableDefiner(BaseTableDefiner):
    def __init__(self, datasource, schema, **kwargs):
        super(MSSQLTableDefiner, self).__init__(datasource, schema, **kwargs)