from .base import BaseTableDefiner
from .db2 import DB2TableDefiner
from .mysql import MySQLTableDefiner
from .mssql import MSSQLTableDefiner
from .postgres import PostgreSQLTableDefiner


DEFINERS = {
    'db2': DB2TableDefiner,
    'mysql': MySQLTableDefiner,
    'mssql': MSSQLTableDefiner,
    'postgres': PostgreSQLTableDefiner
}


class Endpoints(object):
    def __new__(cls, datasource, **kwargs):
        """
        :rtype: BaseTableDefiner
        """
        if datasource._dbname not in DEFINERS:
            raise SyntaxError("Database %s not supported for auto definition of endpoints." % datasource._dbname)

        return DEFINERS[datasource._dbname](datasource, **kwargs)
