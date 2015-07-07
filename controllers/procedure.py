from applications.api.modules.api.request import APIRequest
from applications.api.modules.procedures.base import ProcedureDatasetValidator
from gluon.contrib import simplejson
from procedures import Procedure


def index():
    data = simplejson.loads(request.vars['data'])
    procedure_name = APIRequest.controllerForRewritedURL(request, datasource, True)

    procedure = Procedure()(procedure_name)
    validator = ProcedureDatasetValidator(procedure)
    for row in data:
        if validator.is_valid_dataset(row):
            db.api_procedure_queue.insert(
                name=procedure_name,
                json_data=simplejson.dumps(row)
            )
