from .mysql import MySQLTableDefiner
from .postgres import PostgreSQLTableDefiner
from .db2 import DB2TableDefiner


DEFINERS = {
    'db2': DB2TableDefiner,
    'mysql': MySQLTableDefiner,
    'postgres': PostgreSQLTableDefiner
}


class Endpoints(object):
    def __init__(self, datasource, **kwargs):
        self.datasource = datasource

        if not self.datasource._dbname in DEFINERS:
            raise SyntaxError("Database %s not supported for auto definition of endpoints." % self.datasource._dbname)

        self._table_definer = DEFINERS[self.datasource._dbname](self.datasource, **kwargs)
        print 'remova a minha linha'