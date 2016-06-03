# -*- coding: utf-8 -*-
from api.key import APIKey, APIEndpointPermissions
from api.request import APIRequest
try:
    import httplib as http
except ImportError:
    import http.client as http


def index():
    endpoint = APIRequest.controller_for_path(request.env.PATH_INFO)

    if endpoint not in datasource:
        raise HTTP(http.NOT_FOUND, "Recurso requisitado é inválido")

    api_key = APIKey(db, request.vars.API_KEY)

    if not api_key.auth:
        raise HTTP(http.UNAUTHORIZED, "API Key inválida ou inativa")

    permissions = APIEndpointPermissions(request)
    if permissions.can_perform_api_call():
        api_request = APIRequest(api_key, request)
        return api_request.perform_request()
