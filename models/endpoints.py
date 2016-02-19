# coding=utf-8
from definers import Endpoints
from modelers import JSONModelCreator, Web2pyModelCreator


endpoints_definer = Endpoints(datasource, schema='DBSM')


def load_endpoints(write_models=False, refresh_cache=False):
    if write_models:
        endpoints_definer.add_observer(JSONModelCreator(request.folder + 'private/models.json'))
        endpoints_definer.add_observer(Web2pyModelCreator(request.folder + 'models/'))

    endpoints_definer.define_tables()


if not request.controller == 'rest':
    # if the request isn`t for an endpoint, load everything
    load_endpoints()
