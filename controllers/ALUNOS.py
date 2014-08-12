# -*- coding: utf-8 -*-
from APIKey import APIKey
from APIRequest import APIRequest

@service.json
@service.xml
def index():
	apiKey = APIKey( request.vars.API_KEY )
	if apiKey.auth_key:
		apiRequest = APIRequest( apiKey, request )
		resp = apiRequest.performRequest()

		return resp
	else:
		return dict( error="API Key Inválida" )


def call():
    session.forget()
    return service()

@service.json
@service.xml
def count():
	pass