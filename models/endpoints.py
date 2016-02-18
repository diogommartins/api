# coding=utf-8
from api.request import APIRequest
from definers import Endpoints
from modelers import JSONModelCreator, Web2pyModelCreator


def _lazy():
    """
    Checks if the requested URL was rewritten in `routes.py`. If so, it assumes the requested controller is an ENDPOINT
     and that we should use an `on demand` table definition approach

    :rtype : list
    """
    if request.controller == 'rest':
        return [APIRequest.controller_for_rewrited_URL(request, datasource, lazy=True)]


endpoints_definer = Endpoints(datasource, schema='DBSM')


def load_endpoints(write_models=False, refresh_cache=False):
    if write_models:
        endpoints_definer.add_observer(JSONModelCreator(request.folder + 'private/models.json'))
        endpoints_definer.add_observer(Web2pyModelCreator(request.folder + 'models/'))

    endpoints_definer.define_tables()


if not _lazy():
    load_endpoints()
