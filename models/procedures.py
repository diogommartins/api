from applications.api.modules.procedures import PROCEDURES
from applications.api.modules.procedures.worker import ProcedureWorker


procedure_workers = [ProcedureWorker(db, datasource, procedure, ws_server) for procedure in PROCEDURES.keys()]