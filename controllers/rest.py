# -*- coding: utf-8 -*-
from APIKey import APIKey
from APIRequest import APIRequest
from APIKeyPermissions import APIKeyPermissions


def index():
    apiKey = APIKey(db, request.vars.API_KEY)
    if apiKey.auth:
        keyPermissions = APIKeyPermissions(request)
        if keyPermissions.canPerformAPICall():
            apiRequest = APIRequest(apiKey, request)
            resp = apiRequest.performRequest()
            return resp
    else:
        raise HTTP(403, "API Key Inválida ou Inativa")