# -*- coding: utf-8 -*-
from datetime import datetime

from gluon import current, HTTP
from APIOperation import APIInsert, APIQuery, APIDelete, APIUpdate


class APIRequest(object):
    DEFAULT_SUFIX_SIZE = 4
    validSufixes = ('_MIN', '_MAX', '_BET')
    validResponseFormats = {
        'JSON': 'generic.json',
        'XML': 'generic.xml',
        'HTML': 'generic.html',
        'DEFAULT': 'generic.json'
    }

    def __init__(self, apiKey, request):
        """

        :type request: Request
        :type apiKey: APIKey
        """
        self.request = request
        self.HTTPMethod = self.request.env.request_method
        self.db = current.db
        self.dbSie = current.dbSie
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.apiKey = apiKey  # APIKey
        self.endpoint = self.controllerForRewritedURL()
        self.parameters = self._validateFields()
        self.return_fields = self._validateReturnFields()
        self.validContentTypes = {
            'JSON':     'application/json; charset=%s' % self.db._db_codec,
            'XML':      'text/xml',
            'HTML':     'text/html',
            'DEFAULT':  'application/json; charset=%s' % self.db._db_codec
        }

    @staticmethod
    def controllerForRewritedURL():
        """
        O método retorna o nome do controller requisitado, antes do URL Rewrite realizado
        pelo `routes.py`. Na API, um controller é mapeado diretamente a uma tabela modelado
        e esse nome é utilizado para reconhecer qual tabela foi originalmente requisitada

        Ex.:
            Dada uma requisição `https://sistemas.unirio.br/api/DOC_PESSOAS?API_KEY=xyz`
            request.env.PATH_INFO == '/api/DOC_PESSOAS' -> 'DOC_PESSOAS'

        :rtype : str
        :return: Nome original do controller requisitado
        """
        pathList = current.request.env.PATH_INFO.split("/")
        table = pathList[len(pathList)-1]
        if table in current.dbSie:
            return table
        else:
            raise HTTP(404, 'Recurso requisitado é inválido: ' + table)


    def performRequest(self):
        """
        Método principal, define a ordem e forma de execução de uma requisição a API

        :return: depende do tipo de dado requisitado. Padrão é validResponseFormats['DEFAULT']
        """
        if self.HTTPMethod == "GET":
            req = APIQuery(
                self.endpoint,
                self.parameters,
                self.request.vars,
                self.apiKey,
                self.return_fields
            )  # Cria nova query com os parâmetros processados em APIRequest
            self._defineReturnType()  # Define qual view será usada

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

        self.saveAPIRequest()  # Gera log da requisição
        return req.execute()

    def saveAPIRequest(self):
        """
        Salva a requisição feita pelo usuário no banco.
        Utilizado para auditoria e limitar a quantidade de requisições por API KEY

        """
        def __params():
            params = self.request.vars.copy()
            del params['API_KEY']
            return params

        self.db.api_request.insert(
            dt_request=self.timestamp,
            endpoint=self.endpoint,
            parameters=str(__params()),
            ip=self.request.client,
            auth_key=self.apiKey.auth.id,
            http_method=self.db(self.db.api_methods.http_method == self.HTTPMethod).select(cache=(current.cache.ram, 86400)).first().id
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
            if k in self.dbSie[self.endpoint].fields:
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
            return [field for field in requestedFields if field in self.dbSie[self.endpoint].fields]
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
            if field in self.dbSie[self.endpoint].fields:
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