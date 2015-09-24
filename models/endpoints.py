# coding=utf-8
from api.request import APIRequest
from definers import Endpoints


def _lazy():
    """
    Checks if the requested URL was rewritten in `routes.py`. If so, it assumes the requested controller is an ENDPOINT
     and that we should use an `on demand` table definition approach

    :rtype : list
    """
    if request.controller == 'rest':
        return [APIRequest.controllerForRewritedURL(request, datasource, lazy=True)]

endpoints = Endpoints(datasource, schema='DBSM', lazy_tables=_lazy())
# endpoints = Endpoints(datasource, schema='public')