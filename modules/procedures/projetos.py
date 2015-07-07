from .base import BaseProcedure


class CadastrarProjeto(BaseProcedure):
    def job(self):
        raise NotImplementedError()

    @property
    def required_fields(self):
        raise NotImplementedError()