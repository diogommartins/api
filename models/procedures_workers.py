from procedures import PROCEDURES
from procedures.worker import ProcedureWorker


procedure_workers = [ProcedureWorker(db, datasource, procedure, ws_server) for procedure in PROCEDURES.keys()]

for procedure in procedure_workers:
    procedure.start()
