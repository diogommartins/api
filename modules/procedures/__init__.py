from applications.api.modules.procedures.matricula import MatricularAlunos
from applications.api.modules.procedures.projetos import CadastrarProjeto


PROCEDURES = {
    'MatricularAlunos': MatricularAlunos,
    'CadastrarProjeto': CadastrarProjeto
}


class Procedure(object):
    def __call__(self, name):
        self.name = name
        if self.name not in PROCEDURES:
            raise SyntaxError("Procedure %s not supported." % self.name)

        return PROCEDURES[self.name]
