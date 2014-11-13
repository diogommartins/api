# coding=utf-8
from gluon import current


class APIInsert(object):
    def __init__(self, tablename, parameters):
        self.tablename = tablename
        self.parameters = parameters
        self.db = current.dbSie

    def execute(self):
        return self.db[self.tablename].insert(**self.parameters)