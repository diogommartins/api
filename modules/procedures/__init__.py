from applications.api.modules.procedures.matricula import MatricularAlunos
from applications.api.modules.procedures.projetos import CadastrarProjeto


PROCEDURES = {
    'MatricularAlunos': MatricularAlunos,
    'CadastrarProjeto': CadastrarProjeto
}


class Procedure(object):
    def __call__(self, name):
        """
        Simple `Factory` class for BaseProcedure subclasses that returns a class reference

        :param name: The name of a BaseProcedure subclass
        :raise SyntaxError: Raised when trying to call a nonexistent procedure
        """
        self.name = name
        if self.name not in PROCEDURES:
            raise SyntaxError("Procedure %s not supported." % self.name)

        return PROCEDURES[self.name]
