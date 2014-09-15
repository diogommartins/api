# -*- coding: utf-8 -*-
from gluon import current
class SIEUser():
    def __init__(self):
        self.dbSie = current.dbSie

    def pessoaForCPF(self, cpf):
        cpf = self._addMaskToCPF( cpf )
        pessoa= self.dbSie( (self.dbSie.DOC_PESSOAS.NUMERO_DOCUMENTO == cpf)
                            &(self.dbSie.DOC_PESSOAS.ID_PESSOA == self.dbSie.PESSOAS.ID_PESSOA)
                            &(self.dbSie.DOC_PESSOAS.ID_TDOC_PESSOA == 1) ).select()
        return { 'count' : len( pessoa ), 'content' : pessoa }

    def servidorForCPF(self, cpf):
        pass

    def docenteForCPF(self, cpf):
        return self.dbSie( self.dbSie.V_DOCENTES.CPF == cpf ).select().first()

    def _addMaskToCPF(self,cpf):
        return "%s.%s.%s-%s" % ( cpf[0:3], cpf[3:6], cpf[6:9], cpf[9:11] )