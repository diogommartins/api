# coding=utf-8
from api.request import APIRequest
from definers import Endpoints
from modelers import JSONModelCreator, Web2pyModelCreator


endpoints_definer = Endpoints(datasource, schema='DBSM')


def load_endpoints(write_models=False, refresh_cache=False):
    if write_models:
        endpoints_definer.add_observer(JSONModelCreator(request.folder + 'private/models.json'))
        endpoints_definer.add_observer(Web2pyModelCreator(request.folder + 'models/endpoints/'))

    endpoints_definer.define_tables()


if request.controller == 'rest':
    endpoint = APIRequest.controller_for_path(request.env.PATH_INFO)
    response.models_to_run += ['^endpoints/{endpoint}/\\w+\\.py$'.format(endpoint=endpoint)]
else:
    # if the request isn`t for an endpoint, load everything
    load_endpoints()
