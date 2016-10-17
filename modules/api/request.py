# -*- coding: utf-8 -*-
from datetime import datetime
import thread
from gluon import current, HTTP
from gluon.serializers import json
from .operations import *
from .websockets import WebsocketNotificator
try:
    import httplib as http
except ImportError:
    import http.client as http

__all__ = ['Request']


class Request(object):
    DEFAULT_SUFIX_SIZE = 4
    valid_sufixes = ('_min', '_max', '_bet', '_set',)
    valid_response_formats = {
        'JSON': 'generic.json',
        'XML': 'generic.xml',
        'HTML': 'generic.html',
        'DEFAULT': 'generic.json'
    }
    valid_parameters = ('format', 'fields', 'api_key', 'lmin', 'lmax', 'orderby', 'sort')

    def __init__(self, api_key, request, endpoint, lower_vars):
        """

        :type endpoint: str
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
        self.path_info = self.request.env.PATH_INFO
        self.endpoint = endpoint
        if not self.endpoint:
            raise HTTP(404, "Recurso requisitado é inválido")
        self.lower_vars = lower_vars
        self.parameters = self._validate_fields()
        self.return_fields = self._validate_return_fields()
        self.valid_content_types = {
            'JSON':     'application/json; charset=%s' % self.datasource._db_codec,
            'XML':      'text/xml',
            'HTML':     'text/html',
            'DEFAULT':  'application/json; charset=%s' % self.datasource._db_codec
        }

    @property
    def id_from_path(self):
        """

        :param path: url path
        :return: Um id a ser usado pela chave primária ou None
        """
        path_list = self.path_info.split("/")  # ["", "api", "UNIT_TEST", "123"]
        try:
            uid = path_list[3]  # IndexError = Não tem id.
            return int(uid)     # ValueError = Não é int
        except (IndexError, ValueError):
            return None

    @staticmethod
    def endpoint_for_path(path):
        """
        O método retorna o nome do controller requisitado, antes do URL Rewrite realizado
        pelo `routes.py`. Na API, um controller é mapeado diretamente a uma tabela modelado
        e esse nome é utilizado para reconhecer qual tabela foi originalmente requisitada

        Ex.:
            Dada uma requisição `https://myurl.com/api/ENDPOINT?API_KEY=xyz`
            request.env.PATH_INFO == path == '/api/ENDPOINT' -> 'ENDPOINT'

        >>> Request.endpoint_for_path('/api/UNIT_TEST/123')
        "UNIT_TEST"
        >>> Request.endpoint_for_path('/api/UNIT_TEST')
        "UNIT_TEST"

        :param path: url path
        :rtype : str
        :return: Nome original do controller requisitado
        """
        path_list = path.split("/")  # ["", "api", "UNIT_TEST", "123"]
        endpoint = path_list[2]

        return endpoint.lower()

    @staticmethod
    def procedure_for_path(path):
        """

        >>> Request.procedure_for_path('/api/procedure/FooProcedure')
        "FooProcedure"
        """
        path_list = path.split("/")  # ["", "api", "UNIT_TEST", "123"]
        app_name, controller, procedure_name = path_list[1:]

        assert controller == 'procedure'

        return procedure_name

    def __is_notifyable_operation(self, operation):
        # todo: Isso deveria estar aqui?
        return isinstance(operation, AlterOperation)

    def perform_request(self):
        """
        Método principal, define a ordem e forma de execução de uma requisição a API

        :return: depende do tipo de dado requisitado. Padrão é validResponseFormats['DEFAULT']
        """
        try:
            methods = {
                'GET':      Select,
                'POST':     Insert,
                'PUT':      Update,
                'DELETE':   Delete
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
        for k in self.lower_vars.keys():
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
        if self.lower_vars.fields:
            requested_fields = self.lower_vars.fields.split(",")
            return [field.lower() for field in requested_fields if field.lower() in self.datasource[self.endpoint].fields]
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
        if field.endswith(Request.valid_sufixes):
            return field[:-Request.DEFAULT_SUFIX_SIZE]
