# coding=utf-8
from api.key import Key, ProcedurePermissions
from api.request import Request
from procedures.base import ProcedureDatasetValidator
from gluon.serializers import json, loads_json
from procedures import Procedure
from procedures.exceptions import UndefinedProcedureException, ProcedureException
from datetime import date, datetime
try:
    import httplib as http
except ImportError:
    import http.client as http


def index():
    """
    Responde a requisições do tipo POST para endpoints `procedure/*`

    Dados da requisição devem ter:
    "API_KEY" -> key para obter acesso aos dados.
    "data" -> Lista de dicionários, onde cada dicionário é usado como argumento
    para execução de uma procedure.

    Opcionalmente pode conter:

    'async' -> se requisição será processada de forma assíncrona.
    'fields' - > campos que serão retornados.

    """
    params = loads_json(request.body.read())
    procedure_name = Request.procedure_for_path(request.env.PATH_INFO)

    try:
        procedure = Procedure(procedure_name, datasource)
    except UndefinedProcedureException as e:
        raise HTTP(http.NOT_FOUND, e.msg)

    api_key = Key(db, params['API_KEY'])
    if not api_key.auth:
        raise HTTP(http.UNAUTHORIZED, "API Key inválida ou inativa")

    if not ProcedurePermissions(api_key, procedure_name).can_perform_api_call():
        raise HTTP(http.UNAUTHORIZED, "Nao pode.")

    validator = ProcedureDatasetValidator(procedure)

    try:
        validator = ProcedureDatasetValidator(procedure)
        valid_datasets = tuple(dataset for dataset in params['data'] if validator.is_valid_dataset(dataset))
    except ValueError as e:
        raise HTTP(http.BAD_REQUEST, e.message)  # Invalid dataset

    response.view = 'generic.json'

    for dataset in valid_datasets:
        if params['async']:
            _async(dataset, params, procedure_name)
        else:
            _sync(dataset, params, procedure)


def _async(dataset, params, procedure_name):
    try:
        dataset.update({
            "dt_alteracao": str(date.today()),
            "hr_alteracao": datetime.now().time().strftime("%H:%M:%S"),
            "endereco_fisico": request.env.remote_addr
        })

        db.api_procedure_queue.insert(
            name=procedure_name,
            json_data=json(dataset),
            result_fields=params['fields']
        )
    except Exception as e:
        TicketLogger.log_exception(__file__)  # "Pode haver alguma? O que fazer neste caso ?"


def _sync(dataset, params, procedure):
    try:
        response_dataset = result = procedure.perform_work(dataset,
                                                           commit=True)

        if params['fields']:
            response_dataset = {k: v for k, v in result.iteritems() if k in params['fields']}

        raise HTTP(http.CREATED, json(response_dataset))
    except ProcedureException as e:
        headers = {'error': e.cause}
        raise HTTP(http.INTERNAL_SERVER_ERROR, json(dataset), **headers)
