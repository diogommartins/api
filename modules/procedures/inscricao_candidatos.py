# coding=utf-8
from procedures.base import BaseSIEProcedure, as_transaction


class InscricaoCandidatoPosGraduacao(BaseSIEProcedure):
    COD_TABELA_NACIONALIDADE = 6021
    COD_TABELA_ESTADO_CIVIL = 162
    COD_TABELA_ETNIA = 509
    COD_TABELA_DEFICIENCIA = 229


    @property
    def required_fields(self):
        super_required = super(InscricaoCandidatoPosGraduacao, self).required_fields
        required = {
            'cpf': 'string',  # candidatos
            'id_concurso': 'int',  # inscricoes
            'id_conc_edicao': 'int',  # inscricoes
            'id_opcao': 'int',  # inscricoes
            'id_cota_edicao': 'int',

            'nome_pessoa': 'string',
            'dt_nascimento': 'date',
            'estado_civil_item': 'int',
            'sexo': 'string',
            'nome_pai': 'string',
            'nome_mae': 'string',
            'nacionalidade_item': 'int',
            'deficiencia_item': 'int',
            'tipo_sanguineo': 'string',
            'fator_rh': 'string',
            'cor_item': 'int'

        }
        required.update(super_required)

        return required

    def gerar_num_inscricao(self):
        raise NotImplementedError()

    @property
    def constants(self):
        super_consts = super(InscricaoCandidatoPosGraduacao, self).constants
        consts = {
            'estado_civil_tab': self.COD_TABELA_ESTADO_CIVIL,
            'nacionalidade_tab': self.COD_TABELA_NACIONALIDADE,
            'cor_tab': self.

        }
        consts.update(super_consts)
        return consts

    @as_transaction
    def perform_work(self, dataset, commit=False):
        raise NotImplementedError("Precisa ser implementado")
        return dataset
