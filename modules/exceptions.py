# coding=utf-8
import os
import sys
from gluon.restricted import RestrictedError
from gluon import current


class TicketLogger(object):
    @staticmethod
    def log_exception(fp):
        """
        Copiado de gluon.restricted.RestrictedError.log.
        Encapsula a lógica de criação de ticket para a última exceção capturada.
        :param fp: o file path do arquivo a ser utilizado
        :type fp: str
        """
        def get_code(file_path):
            with open(file_path) as f:
                return f.read()

        fp = os.path.realpath(fp)

        etype, evalue, tb = sys.exc_info()
        # XXX Show exception in Wing IDE if running in debugger
        if __debug__ and 'WINGDB_ACTIVE' in os.environ:
            sys.excepthook(etype, evalue, tb)
        output = "TICKET LOGGER : %s %s" % (etype, evalue)

        RestrictedError(layer=fp, code=get_code(fp), output=output, environment=None).log(current.request)
