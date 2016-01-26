# coding=utf-8
from api.request import APIRequest
from definers import Endpoints
from modelers import JSONModelCreator


def _lazy():
    """
    Checks if the requested URL was rewritten in `routes.py`. If so, it assumes the requested controller is an ENDPOINT
     and that we should use an `on demand` table definition approach

    :rtype : list
    """
    if request.controller == 'rest':
        return [APIRequest.controllerForRewritedURL(request, datasource, lazy=True)]

model_creator = JSONModelCreator(request.folder + 'private/models.json')
endpoints = Endpoints(datasource, schema='DBSM', lazy_tables=_lazy(), observer=model_creator)
