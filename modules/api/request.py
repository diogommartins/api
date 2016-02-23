# -*- coding: utf-8 -*-
from datetime import datetime
import thread
from gluon import current, HTTP
from gluon.serializers import json
from .operations import APIInsert, APIQuery, APIDelete, APIUpdate, APIAlterOperation
from .websockets import WebsocketNotificator
try:
    import httplib as http
except ImportError:
    import http.client as http

__all__ = ['APIRequest']


class APIRequest(object):
    DEFAULT_SUFIX_SIZE = 4
    valid_sufixes = ('_MIN', '_MAX', '_BET', '_SET',)
    valid_response_formats = {
        'JSON': 'generic.json',
        'XML': 'generic.xml',
        'HTML': 'generic.html',
        'DEFAULT': 'generic.json'
    }
    valid_parameters = ('FORMAT', 'FIELDS', 'API_KEY', 'LMIN', 'LMAX', 'ORDERBY', 'SORT')

    def __init__(self, api_key, request):
        """

        :type request: Request
        :type api_key: key.APIKey
        """
        self.request = request
        self.HTTPMethod = self.request.env.request_method
        self.db = current.db
        self.cache = (current.cache.ram, 86400)
        self.datasource = current.datasource
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.api_key = api_key
        self.endpoint = self.controller_for_rewrited_URL(self.request)
        if not self.endpoint:
            raise HTTP(404, "Recurso requisitado é inválido")

        self.parameters = self._validate_fields()
        self.return_fields = self._validate_return_fields()
        self.valid_content_types = {
            'JSON':     'application/json; charset=%s' % self.datasource._db_codec,
            'XML':      'text/xml',
            'HTML':     'text/html',
            'DEFAULT':  'application/json; charset=%s' % self.datasource._db_codec
        }

    @staticmethod
    def controller_for_rewrited_URL(request):
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
        path_list = request.env.PATH_INFO.split("/")
        endpoint = path_list[len(path_list)-1]

        return endpoint

    def __is_notifyable_operation(self, operation):
        # todo: Isso deveria estar aqui?
        return isinstance(operation, APIAlterOperation)

    def perform_request(self):
        """
        Método principal, define a ordem e forma de execução de uma requisição a API

        :return: depende do tipo de dado requisitado. Padrão é validResponseFormats['DEFAULT']
        """
        try:
            methods = {
                'GET':      APIQuery,
                'POST':     APIInsert,
                'PUT':      APIUpdate,
                'DELETE':   APIDelete
            }
            operation = methods[self.HTTPMethod](self)
        except KeyError:
            raise HTTP(http.METHOD_NOT_ALLOWED, "Método não suportado")

        thread.start_new_thread(self.__save_log, tuple())

        self._define_response_return_type()

        if self.__is_notifyable_operation(operation):
            operation.observer = WebsocketNotificator()

        return operation.execute()

    def __save_log(self):
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
            auth_key=self.api_key.auth.id,
            http_method=self.db(self.db.api_methods.http_method == self.HTTPMethod).select(cache=self.cache).first().id
        )
        self.db.commit()

    def _define_response_return_type(self):
        """
        Define o formato de resposta (HTML,XML,JSON,..) de acordo com o parâmetro
        requisitado pelo usuário, setando a view correspondente que será utilizada
        e o Content-Type adequado.

        """

        if self.HTTPMethod == 'GET':
            response = current.response
            response_format = self.request.vars.FORMAT
            if response_format in self.valid_response_formats:
                response.view = self.valid_response_formats[response_format]
                response.headers['Content-Type'] = self.valid_content_types[response_format]
            else:
                response.view = self.valid_response_formats['DEFAULT']
                response.headers['Content-Type'] = self.valid_content_types['DEFAULT']

    def _validate_fields(self):
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
        endpoint_fields = self.datasource[self.endpoint].fields
        fields = {"valid": [], "special": []}
        invalid_fields = []
        for k, v in self.request.vars.iteritems():
            if k in endpoint_fields:
                fields['valid'].append(k)
            elif self._is_valid_field_with_sufix(k):
                fields['special'].append(k)
            else:
                if k not in self.valid_parameters:
                    invalid_fields.append(k)
        if invalid_fields:
            headers = {"InvalidParameters": json(invalid_fields)}
            raise HTTP(http.BAD_REQUEST, "Alguns parâmetros da requisição são incompatíveis.", **headers)
        return fields

    def _validate_return_fields(self):
        """
        Método para verificar se os parâmetros de retorno passados são válidos.
        Retorna uma lista com os FIELDS válidos ou uma lista vazia, que é interpretada
        como todas as colunas.

        :rtype : list
        :return: Retorna uma lista contendo somente os itens da lista que forem colunas na tabela requisitada
        """
        if self.request.vars["FIELDS"]:
            requested_fields = self.request.vars["FIELDS"].split(",")
            return [field for field in requested_fields if field in self.datasource[self.endpoint].fields]
        else:
            return []

    def _is_valid_field_with_sufix(self, field):
        """
        Campos especiais são strings contidas na lista de colunas de uma tabela,
        acrescidas de um sufixo válido, como _MIN, _MAX, etc. Esse método verifica
        se o campo passado está dentro desta categoria.

        :rtype : bool
        :param field: Uma string reference a um campo
        :return: True se for um campo um campo válido, acrescido de um sufixo válido
        """
        chopped_field = self.special_field_chop(field)
        if chopped_field and chopped_field in self.datasource[self.endpoint].fields:
            return True

    @staticmethod
    def special_field_chop(field):
        """
        Dada uma string fornecida como entrada, o método valida o sufixo e retorna
        o campo correspondente, sem o sufixo.

        :param field: Uma string reference a um campo, com sufixo
        :return: Uma string relativa a um campo, sem sufixo
        """
        if field.endswith(APIRequest.valid_sufixes):
            return field[:-APIRequest.DEFAULT_SUFIX_SIZE]