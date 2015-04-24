# coding=utf-8
from definers import Endpoints
from APIRequest import APIRequest


def _lazy():
    """
    Checks if the requested URL was rewritten in routes.py, if so, it assumes the requested controller is an ENDPOINT
     and that we should use an `on demand` table definition approach

    :rtype : list
    """
    if request.env.PATH_INFO != request.env.path_info:
        return [APIRequest.controllerForRewritedURL(request, datasource, lazy=True)]

endpoints = Endpoints(datasource, schema='DBSM', lazy_tables=_lazy())
# endpoints = Endpoints(datasource, schema='public')