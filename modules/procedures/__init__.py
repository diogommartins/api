# coding=utf-8
from .exceptions import UndefinedProcedureException
from .matricula import MatricularAlunos
from .projetos import CriarProjetoPesquisa, RegistroProjetoPesquisa, FechaAvaliacaoProjetosPesquisa, AbrirAvaliacaoProjetosPesquisa
from .documento import CriarDocumentoProjetoPesquisa
from .enderecos import CriarEndereco
from .grafos import TramitacoesComoGrafo
from .base import BaseProcedure
from .test import FooProcedure
# from .pessoas import *
from .funcionarios import *
from .inscricao_candidatos import *
from inspect import isclass


def is_callable_procedure(t):
    """
    :type t: type
    """
    return isclass(t) and issubclass(t, BaseProcedure) and t != BaseProcedure

PROCEDURES = {k: v for k, v in globals().iteritems() if is_callable_procedure(v)}


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
