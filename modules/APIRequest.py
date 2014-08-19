# -*- coding: utf-8 -*-
from gluon import current
from APIKey import APIKey
from APIQuery import APIQuery
from datetime import datetime

class APIRequest():
    def __init__( self, apiKey, request ):
        self.request = request
        self.db = current.db
        self.dbSie = current.dbSie
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.apiKey = apiKey # APIKey
        self.parameters = self._validateFields()
        self.table = request.controller

    def performRequest(self):
        query = APIQuery(
                         self.request.controller,
                         self.parameters['valid'],
                         self.request.vars
                        )
        self.saveAPIRequest()
        return query.execute()

    def saveAPIRequest(self):
        self.db.api_request.insert(
                              dt_request = self.timestamp,
                              url = self.request.env.request_uri,
                              ip = self.request.client,
                              auth_key = self.apiKey.auth_key.id
                              )
        self.db.commit()

    # Método que verifica se os parâmetros passados são válidos ou não
    def _validateFields(self):
        fields = { "valid" : [], "invalid" : [] }
        for k, v in self.request.vars.iteritems():
            if k in self.dbSie[self.request.controller].fields:
                fields['valid'].append(k)
            else:
                fields['invalid'].append(k)

        return fields