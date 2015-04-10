# coding=utf-8


class BaseTableDefiner(object):
    types = {}

    def __init__(self, datasource, schema, cache_model=current.cache.ram, cacheTime=86400, verbose=False):
        self.db = datasource
        self.schema = schema
        self.cache = cache_model
        self.cacheTime = cacheTime
        self.verbose = verbose