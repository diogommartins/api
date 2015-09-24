# coding=utf-8
from api.request import APIRequest
from procedures.base import ProcedureDatasetValidator
from gluon.contrib import simplejson
from procedures import Procedure
from datetime import date, datetime


def index():
    """
    Responde a requisições do tipo POST para endpoints `procedure/*`

    """
    data = simplejson.loads(request.vars['data'])
    procedure_name = APIRequest.controllerForRewritedURL(request, datasource, True)

    procedure = Procedure()(procedure_name)
    validator = ProcedureDatasetValidator(procedure)
    for row in data:
        if validator.is_valid_dataset(row):
            try:
                row.update({
                    "CONCORRENCIA": 999,
                    "DT_ALTERACAO": str(date.today()),
                    "HR_ALTERACAO": datetime.now().time().strftime("%H:%M:%S"),
                    "ENDERECO_FISICO": request.env.remote_addr,
                    "COD_OPERADOR": 1  # DBSM.USUARIOS.ID_USUARIO admin
                })

                db.api_procedure_queue.insert(
                    name=procedure_name,
                    json_data=simplejson.dumps(row)
                )
            except Exception as e:
                pass