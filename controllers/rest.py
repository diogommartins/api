# -*- coding: utf-8 -*-
from api.key import APIKey, APIKeyPermissions
from api.request import APIRequest
try:
    import httplib as http
except ImportError:
    import http.client as http


def index():
    apiKey = APIKey(db, request.vars.API_KEY)
    if apiKey.auth:
        keyPermissions = APIKeyPermissions(request)
        if keyPermissions.canPerformAPICall():
            apiRequest = APIRequest(apiKey, request)
            return apiRequest.perform_request()
    else:
        raise HTTP(http.UNAUTHORIZED, "API Key inválida ou inativa")
