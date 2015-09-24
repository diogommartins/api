# coding=utf-8
from applications.api.modules.procedures.exceptions import UndefinedProcedureException


def procedure():
    try:
        procedure_name = request.args[0]
        procedure = PROCEDURES[procedure_name]
        queue = db.api_procedure_queue

        finished = db((queue.dt_conclusion!=None) & (queue.name==procedure_name) & (queue.did_finish_correctly==True)).select(
            queue.resulting_dataset,
            queue.dt_conclusion
        )

        errors = db((queue.dt_conclusion!=None) & (queue.name==procedure_name) & (queue.did_finish_correctly==False)).select(
            queue.resulting_dataset,
            queue.status_description,
            queue.dt_conclusion
        )

        return dict(
            required_fields=procedure.required_fields.keys(),
            finished=finished,
            errors=errors,
            ws_group=procedure_name
        )
    except KeyError as e:
        raise UndefinedProcedureException(request.args[0] + " não é uma procedure válida", e)
