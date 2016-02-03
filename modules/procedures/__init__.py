# coding=utf-8
from .exceptions import UndefinedProcedureException
from .matricula import MatricularAlunos
from .projetos import CriarProjetoPesquisa, RegistroProjetoPesquisa
from .documento import CriarDocumentoProjetoPesquisa
from .base import BaseProcedure

# todo: Otimizar essa porra ou essa é uma boa implementação ?
PROCEDURES = {
    'MatricularAlunos': MatricularAlunos,
    'CriarDocumentoProjetoPesquisa': CriarDocumentoProjetoPesquisa,
    'CriarProjetoPesquisa': CriarProjetoPesquisa,
    'RegistroProjetoPesquisa': RegistroProjetoPesquisa
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
