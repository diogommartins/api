# coding=utf-8
from .base import BaseProcedure


class FooProcedure(BaseProcedure):
    """
    Não faz nada e existe somente para fins de teste.
    """
    @property
    def required_fields(self):
        return {
            'ID_UNIT_TEST': 'int'
        }

    @property
    def constants(self):
        return {'output': 'foo'}

    def perform_work(self, dataset, commit=True):
        dataset.update(self.constants)
        return dataset
