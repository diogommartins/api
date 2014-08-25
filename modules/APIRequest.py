# -*- coding: utf-8 -*-
from gluon import current
from APIKey import APIKey
from APIQuery import APIQuery
from datetime import datetime

class APIRequest():
    validSufixes = ('_MIN', '_MAX', '_BET')
    validResponseFormats = {
                           'JSON' : 'generic.json',
                           'XML' : 'generic.xml',
                           'HTML' : 'generic.html',
                           'DEFAULT' : 'generic.html'
                           }

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
                         self.parameters,
                         self.request.vars
                        )
        self.saveAPIRequest()
        self._defineReturnType()
        return query.execute()

    def saveAPIRequest(self):
        self.db.api_request.insert(
                              dt_request = self.timestamp,
                              url = self.request.env.request_uri,
                              ip = self.request.client,
                              auth_key = self.apiKey.auth_key.id
                              )
        self.db.commit()

    def _defineReturnType(self):
        format = self.request.vars.FORMAT
        if format in APIRequest.validResponseFormats:
            current.response.view = APIRequest.validResponseFormats[ format ]
        else:
            current.response.view = APIRequest.validResponseFormats[ 'DEFAULT' ]

    # Método que verifica se os parâmetros passados são válidos ou não
    def _validateFields(self):
        fields = { "valid" : [], "special" : [], "invalid" : [] }
        for k, v in self.request.vars.iteritems():
            if k in self.dbSie[self.request.controller].fields:
                fields['valid'].append( k )
            elif self._isValidFieldWithSufix( k ):
                fields['special'].append( k )
            else:
                fields['invalid'].append( k )

        return fields

    def _isValidFieldWithSufix(self, field):
        if self.specialFieldChop(field):
            field = self.specialFieldChop(field)
            if field in self.dbSie[self.request.controller].fields:
                return True
        return False

    # Método para cortar e validar o sufixo de uma string de field caso ela termine com _MIN ou _MAX, etc e
    @staticmethod
    def specialFieldChop(field):
        DEFAULT_SUFIX_SIZE = 4
        if field.endswith( APIRequest.validSufixes ):
            return field[:-DEFAULT_SUFIX_SIZE]
        return False