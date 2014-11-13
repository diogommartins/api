# -*- coding: utf-8 -*-
from gluon import current, HTTP
from APIKey import APIKey
from APIQuery import APIQuery
from APIInsert import APIInsert
from datetime import datetime


class APIRequest():
    DEFAULT_SUFIX_SIZE = 4
    validSufixes = ('_MIN', '_MAX', '_BET')
    validResponseFormats = {
        'JSON': 'generic.json',
        'XML': 'generic.xml',
        'HTML': 'generic.html',
        'DEFAULT': 'generic.html'
    }
    validContentTypes = {
        'JSON': 'text/json',
        'XML': 'text/xml',
        'HTML': 'text/html',
        'DEFAULT': 'text/html'
    }

    def __init__(self, apiKey, request):
        self.request = request
        self.db = current.db
        self.dbSie = current.dbSie
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.apiKey = apiKey  # APIKey

        self.tablename = self.controllerForRewritedURL()
        self.parameters = self._validateFields()
        self.return_fields = self._validateReturnFields()

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
        if self.request.env.request_method == "GET":
            req = APIQuery(
                self.tablename,
                self.parameters,
                self.request.vars,
                self.return_fields
            )  # Cria nova query com os parâmetros processados em APIRequest
            self.saveAPIRequest()  # Gera log da query
            self._defineReturnType()  # Define qual view será usada
            return req.execute()  # Executa e retorna a query

        elif self.request.env.request_method == "POST":
            req = APIInsert(
                self.tablename,
                self.parameters
            )

        self.saveAPIRequest()  # Gera log da query
        return req.execute()  # Executa e retorna a query

    def saveAPIRequest(self):
        """
        Salva a requisição feita pelo usuário no banco.
        Utilizado para auditoria e limitar a quantidade de requisições por API KEY

        """
        self.db.api_request.insert(
            dt_request=self.timestamp,
            url=self.request.env.request_uri,
            ip=self.request.client,
            auth_key=self.apiKey.auth_key.id
        )
        self.db.commit()

    def _defineReturnType(self):
        """
        Define o formato de resposta (HTML,XML,JSON,..) de acordo com o parâmetro
        requisitado pelo usuário, setando a view correspondente que será utilizada
        e o Content-Type adequado.

        """
        format = self.request.vars.FORMAT
        if format in APIRequest.validResponseFormats:
            current.response.view = APIRequest.validResponseFormats[format]
            current.response.headers['Content-Type'] = APIRequest.validContentTypes[format]
        else:
            current.response.view = APIRequest.validResponseFormats['DEFAULT']
            current.response.headers['Content-Type'] = APIRequest.validContentTypes['DEFAULT']


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
            if k in self.dbSie[self.tablename].fields:
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
            return [field for field in requestedFields if field in self.dbSie[self.tablename].fields]
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
            if field in self.dbSie[self.tablename].fields:
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