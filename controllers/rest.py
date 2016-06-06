# -*- coding: utf-8 -*-
from api.key import APIKey, APIEndpointPermissions
from api.request import APIRequest
try:
    import httplib as http
except ImportError:
    import http.client as http
from gluon.storage import Storage


def index():
    endpoint = APIRequest.endpoint_for_path(request.env.PATH_INFO)

    if endpoint not in datasource:
        raise HTTP(http.NOT_FOUND, "Recurso requisitado é inválido")

    # case insensitive todo: Necessário, mas provavelmente não deveria estar aqui
    lower_vars = Storage({k.lower(): v for k, v in request.vars.iteritems()})

    api_key = APIKey(db, lower_vars.api_key)

    if not api_key.auth:
        raise HTTP(http.UNAUTHORIZED, "API Key inválida ou inativa")

    fields = []
    if lower_vars.fields:
        # case insensitive
        fields = [field.lower() for field in lower_vars.fields.split(",")]

    permissions = APIEndpointPermissions(endpoint, api_key, request.env.request_method, fields)
    if permissions.can_perform_api_call():
        api_request = APIRequest(api_key, request, endpoint, lower_vars)
        return api_request.perform_request()
