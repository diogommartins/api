# -*- coding: utf-8 -*-
from gluon import current
from APIKey import APIKey
from APIQuery import APIQuery
from datetime import datetime

class APIRequest():
    DEFAULT_SUFIX_SIZE = 4
    validSufixes = ('_MIN', '_MAX', '_BET')
    validResponseFormats = {
                           'JSON' : 'generic.json',
                           'XML' : 'generic.xml',
                           'HTML' : 'generic.html',
                           'DEFAULT' : 'generic.html'
                           }
    validContentTypes = {
                         'JSON' : 'text/json',
                         'XML' : 'text/xml',
                         'HTML' : 'text/html',
                         'DEFAULT' : 'text/html'
                         }

    def __init__( self, apiKey, request ):
        self.request = request
        self.db = current.db
        self.dbSie = current.dbSie
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.apiKey = apiKey # APIKey
        self.parameters = self._validateFields()
        self.table = request.controller
        self.return_fields = self._validateReturnFields()

    #===========================================================================
    # Método principal, define a ordem e forma de execução de uma requisição a API
    # Return: depende do tipo de dado requisitado. Padrão é validResponseFormats['DEFAULT']
    #===========================================================================
    def performRequest(self):

        query = APIQuery(
                         self.request.controller,
                         self.parameters,
                         self.request.vars,
                         self.return_fields
                        )           # Cria nova query com os parâmetros processados em APIRequest
        self.saveAPIRequest()       # Gera log da query
        self._defineReturnType()    # Define qual view será usada
        return query.execute()      # Executa e retorna a query

    #===========================================================================
    # Salva a requisição feita pelo usuário no banco. Utilizado para auditoria
    # e limitar a quantidade de requisições por API KEY
    #===========================================================================
    def saveAPIRequest(self):
        self.db.api_request.insert(
                              dt_request = self.timestamp,
                              url = self.request.env.request_uri,
                              ip = self.request.client,
                              auth_key = self.apiKey.auth_key.id
                              )
        self.db.commit()

    #===============================================================================
    # Define o formato de resposta (HTML,XML,JSON,..) de acordo com o parâmetro requisitado pelo usuário
    #===============================================================================
    def _defineReturnType(self):
        format = self.request.vars.FORMAT
        if format in APIRequest.validResponseFormats:
            current.response.view = APIRequest.validResponseFormats[ format ]
            current.response.headers['Content-Type'] = APIRequest.validContentTypes[ format ]
        else:
            current.response.view = APIRequest.validResponseFormats[ 'DEFAULT' ]
            current.response.headers['Content-Type'] = APIRequest.validContentTypes[ 'DEFAULT' ]

    #==========================================================================
    # Método que verifica se os parâmetros passados são válidos ou não
    #==========================================================================
    def _validateFields(self):
        fields = { "valid" : [], "special" : [] }
        for k, v in self.request.vars.iteritems():
            if k in self.dbSie[self.request.controller].fields:
                fields['valid'].append( k )
            elif self._isValidFieldWithSufix( k ):
                fields['special'].append( k )

        return fields

    #===========================================================================
    # Método para verificar se os parâmetros de retorno passados são válidos
    #
    # Retorna uma lista com os FIELDS válidos ou uma lista vazia, que é interpretada
    # como todas as colunas
    #===========================================================================
    def _validateReturnFields(self):
        if self.request.vars["FIELDS"]:
            requestedFields = self.request.vars["FIELDS"].split(",")
            # Retorna uma lista contendo somente os itens da lista que forem colunas na tabela requisitada
            return[ field for field in requestedFields if field in self.dbSie[self.request.controller].fields ]
        else:
            return[]

    #===========================================================================
    # Tipos especiais como Datas e Floats podem ser utilizados com o sufixo _MIN
    # _MAX, etc. Esse método verifica se o campo passado está dentro desta categoria
    # Return: Boolean
    #===========================================================================
    def _isValidFieldWithSufix(self, field):
        if self.specialFieldChop(field):
            field = self.specialFieldChop(field)
            if field in self.dbSie[self.request.controller].fields:
                return True
        return False

    #===========================================================================
    # Método para cortar e validar o sufixo de uma string de field caso ela
    # termine com _MIN ou _MAX, etc e
    #===========================================================================
    @staticmethod
    def specialFieldChop(field):
        if field.endswith( APIRequest.validSufixes ):
            return field[ :-APIRequest.DEFAULT_SUFIX_SIZE ]
        return False