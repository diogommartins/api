# -*- coding: utf-8 -*-
from api.key import APIKey, APIKeyPermissions
from api.request import APIRequest


def index():
    apiKey = APIKey(db, request.vars.API_KEY)
    if apiKey.auth:
        keyPermissions = APIKeyPermissions(request)
        if keyPermissions.canPerformAPICall():
            apiRequest = APIRequest(apiKey, request)
            return apiRequest.performRequest()
    else:
        raise HTTP(403, "API Key inválida ou inativa")