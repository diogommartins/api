# coding=utf-8
from api.request import Request
from definers import Endpoints
from modelers import JSONModelCreator, Web2pyModelCreator


prefixes = tuple(p.prefix for p in db().select(db.api_blacklist.prefix))
endpoints_definer = Endpoints(datasource, schema='DBSM', blacklist=prefixes)


def load_endpoints(write_models=True):
    if write_models:
        endpoints_definer.add_observer(JSONModelCreator(request.folder + 'private/', 'models.json'))
        endpoints_definer.add_observer(Web2pyModelCreator(request.folder + 'models/endpoints/'))

    endpoints_definer.define_tables()


if request.controller == 'rest':
    endpoint = Request.endpoint_for_path(request.env.PATH_INFO)
    response.models_to_run += ['^endpoints/{endpoint}/\\w+\\.py$'.format(endpoint=endpoint)]
else:
    # if the request isn`t for an endpoint, load everything
    load_endpoints()
