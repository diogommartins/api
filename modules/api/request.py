# -*- coding: utf-8 -*-
from datetime import datetime
import thread
from gluon import current, HTTP
from .operations import APIInsert, APIQuery, APIDelete, APIUpdate


__all__ = ['APIRequest']


class APIRequest(object):
    DEFAULT_SUFIX_SIZE = 4
    validSufixes = ('_MIN', '_MAX', '_BET', '_SET')
    validResponseFormats = {
        'JSON': 'generic.json',
        'XML': 'generic.xml',
        'HTML': 'generic.html',
        'DEFAULT': 'generic.json'
    }

    def __init__(self, apiKey, request):
        """

        :type request: Request
        :type apiKey: key.APIKey
        """
        self.request = request
        self.HTTPMethod = self.request.env.request_method
        self.db = current.db
        self.cache = (current.cache.ram, 86400)
        self.datasource = current.datasource
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.apiKey = apiKey
        self.endpoint = self.controllerForRewritedURL(self.request, self.datasource)
        if not self.endpoint:
            raise HTTP(404, "Recurso requisitado é inválido")

        self.parameters = self._validateFields()
        self.return_fields = self._validateReturnFields()
        self.validContentTypes = {
            'JSON':     'application/json; charset=%s' % self.datasource._db_codec,
            'XML':      'text/xml',
            'HTML':     'text/html',
            'DEFAULT':  'application/json; charset=%s' % self.datasource._db_codec
        }

    @staticmethod
    def controllerForRewritedURL(request, db, lazy=False):
        """
        O método retorna o nome do controller requisitado, antes do URL Rewrite realizado
        pelo `routes.py`. Na API, um controller é mapeado diretamente a uma tabela modelado
        e esse nome é utilizado para reconhecer qual tabela foi originalmente requisitada

        Ex.:
            Dada uma requisição `https://myurl.com/api/ENDPOINT?API_KEY=xyz`
            request.env.PATH_INFO == '/api/ENDPOINT' -> 'ENDPOINT'

        :rtype : str
        :return: Nome original do controller requisitado
        """
        pathList = request.env.PATH_INFO.split("/")
        resource = pathList[len(pathList)-1]
        if resource in db or lazy:
            return resource

    def performRequest(self):
        """
        Método principal, define a ordem e forma de execução de uma requisição a API

        :return: depende do tipo de dado requisitado. Padrão é validResponseFormats['DEFAULT']
        """
        if self.HTTPMethod == "GET":
            req = APIQuery(self)        # Cria query com os parâmetros processados em APIRequest
            self._defineReturnType()    # Define qual view será usada
        elif self.HTTPMethod == "POST":
            req = APIInsert(
                self.endpoint,
                self.parameters
            )
        elif self.HTTPMethod == "PUT":
            req = APIUpdate(
                self.endpoint,
                self.parameters
            )
        elif self.HTTPMethod == "DELETE":
            req = APIDelete(
                self.endpoint,
                self.parameters
            )
        # Gera log da requisição
        thread.start_new_thread(self.__saveAPIRequest, tuple())

        return req.execute()

    def __saveAPIRequest(self):
        """
        Salva a requisição feita pelo usuário no banco.
        Utilizado para auditoria e limitar a quantidade de requisições por API KEY

        """
        def __params():
            params = self.request.vars.copy()
            del params['API_KEY']
            return params
        #TODO Pode ser realizado em
        self.db.api_request.insert(
            dt_request=self.timestamp,
            endpoint=self.endpoint,
            parameters=str(__params()),
            ip=self.request.client,
            auth_key=self.apiKey.auth.id,
            http_method=self.db(self.db.api_methods.http_method == self.HTTPMethod).select(cache=self.cache).first().id
        )
        self.db.commit()

    def _defineReturnType(self):
        """
        Define o formato de resposta (HTML,XML,JSON,..) de acordo com o parâmetro
        requisitado pelo usuário, setando a view correspondente que será utilizada
        e o Content-Type adequado.

        """
        format = self.request.vars.FORMAT
        if format in self.validResponseFormats:
            current.response.view = self.validResponseFormats[format]
            current.response.headers['Content-Type'] = self.validContentTypes[format]
        else:
            current.response.view = self.validResponseFormats['DEFAULT']
            current.response.headers['Content-Type'] = self.validContentTypes['DEFAULT']


    def _validateFields(self):
        """
        Método que verifica se os parâmetros passados são válidos ou não. Um dicionário
        com duas chaves é retornado:

        `valid` uma lista de campos cujos nomes estão contidos na lista de colunas da
        tabela requisitada
        `special` uma lista de campos cujos nomes, com um sufixo válido, estão contidos
        na lista de colunas da tabela requisitada

        :rtype : dict
        :return: Um dicionário contendo os campos válidos
        """
        fields = {"valid": [], "special": []}
        for k, v in self.request.vars.iteritems():
            if k in self.datasource[self.endpoint].fields:
                fields['valid'].append(k)
            elif self._isValidFieldWithSufix(k):
                fields['special'].append(k)

        return fields

    def _validateReturnFields(self):
        """
        Método para verificar se os parâmetros de retorno passados são válidos.
        Retorna uma lista com os FIELDS válidos ou uma lista vazia, que é interpretada
        como todas as colunas.

        :rtype : list
        :return: Retorna uma lista contendo somente os itens da lista que forem colunas na tabela requisitada
        """
        if self.request.vars["FIELDS"]:
            requestedFields = self.request.vars["FIELDS"].split(",")
            return [field for field in requestedFields if field in self.datasource[self.endpoint].fields]
        else:
            return []

    def _isValidFieldWithSufix(self, field):
        """
        Campos especiais são strings contidas na lista de colunas de uma tabela,
        acrescidas de um sufixo válido, como _MIN, _MAX, etc. Esse método verifica
        se o campo passado está dentro desta categoria.

        :rtype : bool
        :param field: Uma string reference a um campo
        :return: True se for um campo um campo válido, acrescido de um sufixo válido
        """
        if self.specialFieldChop(field):
            field = self.specialFieldChop(field)
            if field in self.datasource[self.endpoint].fields:
                return True

    @staticmethod
    def specialFieldChop(field):
        """
        Dada uma string fornecida como entrada, o método valida o sufixo e retorna
        o campo correspondente, sem o sufixo.

        :param field: Uma string reference a um campo, com sufixo
        :return: Uma string relativa a um campo, sem sufixo
        """
        if field.endswith(APIRequest.validSufixes):
            return field[:-APIRequest.DEFAULT_SUFIX_SIZE]