from .exceptions import UndefinedProcedureException
from .matricula import MatricularAlunos
from .projetos import CadastrarProjeto
from .documento import CriarDocumentoProjetoPesquisa
from .base import BaseProcedure


PROCEDURES = {
    'MatricularAlunos': MatricularAlunos,
    # 'CadastrarProjeto': CadastrarProjeto
    'CriarDocumentoProjetoPesquisa': CriarDocumentoProjetoPesquisa
}


class Procedure(object):
    def __new__(cls, name, datasource):
        """
        Simple `Factory` class for BaseProcedure subclasses that returns a class reference

        :type datasource: gluon.dal.DAL
        :param name: The name of a BaseProcedure subclass
        :raise SyntaxError: Raised when trying to call a nonexistent procedure
        :rtype: BaseProcedure
        """
        try:
            return PROCEDURES[name](datasource)
        except KeyError as e:
            raise UndefinedProcedureException("Procedure %s not supported." % name, e)
