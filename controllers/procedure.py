# coding=utf-8
from api.request import APIRequest
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

    """
    params = loads_json(request.body.read())
    procedure_name = APIRequest.controller_for_rewrited_URL(request, datasource, True)

    try:
        procedure = Procedure(procedure_name, datasource)
    except UndefinedProcedureException as e:
        raise HTTP(http.BAD_REQUEST, e.msg)

    validator = ProcedureDatasetValidator(procedure)

    for dataset in params['data']:
        if validator.is_valid_dataset(dataset):
            if params['async']:
                _async(dataset, params, procedure_name)
            else:
                _sync(dataset, params, procedure)

        else:
            raise NotImplementedError("Possui dataset inválido...")


def _async(dataset, params, procedure_name):
    try:
        dataset.update({
            "DT_ALTERACAO": str(date.today()),
            "HR_ALTERACAO": datetime.now().time().strftime("%H:%M:%S"),
            "ENDERECO_FISICO": request.env.remote_addr
        })

        db.api_procedure_queue.insert(
                name=procedure_name,
                json_data=json(dataset),
                result_fields=params['fields']
        )
    except Exception as e:
        raise NotImplementedError("Pode haver alguma? O que fazer neste caso ?")


def _sync(dataset, params, procedure):
    try:
        response_dataset = result = procedure.perform_work(dataset)

        if params['fields']:
            response_dataset = {k: v for k, v in result.iteritems() if k in params['fields']}

        raise HTTP(http.CREATED, json(response_dataset))
    except ProcedureException as e:
        headers = {'error': e.cause}
        raise HTTP(http.INTERNAL_SERVER_ERROR, json(dataset), **headers)
