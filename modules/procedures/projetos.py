from datetime import date
from .documento import CriarDocumentoProjetoPesquisa
from .base import BaseSIEProcedure, as_transaction


class CadastrarProjeto(CriarDocumentoProjetoPesquisa):
    @property
    def required_fields(self):
        super_required = super(CriarDocumentoProjetoPesquisa, self).required_fields
        required = {
            'TITULO': 'string',
            'DT_INICIAL': 'date',
            'DT_REGISTRO': 'date',
            'TIPO_PUBLICO_TAB': 'int',
            'TIPO_PUBLICO_ITEM': 'int',
            'ACESSO_PARTICIP': 'string',
            'EVENTO_TAB': 'int',
            'EVENTO_ITEM': 'int',
            'PAGA_BOLSA': 'string',
            'TEM_APOIO_FINANCEIO': 'bool'
        }
        required.update(super_required)
        return required


class CriarProjetoPesquisa(CadastrarProjeto):
    @property
    def constants(self):
        super_consts = super(CriarDocumentoProjetoPesquisa, self).constants
        consts = {
            "EVENTO_TAB": self.COD_TABELA_TIPO_EVENTO,
            "EVENTO_ITEM": self.ITEM_TIPO_EVENTO_NAO_SE_APLICA,
            "TIPO_PUBLICO_TAB": self.COD_TABELA_TIPO_PUBLICO_ALVO,
            "TIPO_PUBLICO_ITEM": self.ITEM_TIPO_PUBLICO_3_GRAU,
            "ACESSO_PARTICIP": self.ACESSO_PARTICIPANTES_APENAS_COORDENADOR,
            "PAGA_BOLSA": self.NAO_PAGA_BOLSA,
            "AVALIACAO_TAB": self.COD_TABELA_AVALIACAO_PROJETOS_INSTITUICAO,
            "AVALIACAO_ITEM": self.ITEM_AVALIACAO_PROJETOS_INSTITUICAO_NAO_AVALIADO,
            'ID_CLASSIFICACAO': self.ITEM_CLASSIFICACAO_PROJETO_PESQUISA,
            'SITUACAO_TAB': self.COD_TABELA_SITUACAO,
            'SITUACAO_ITEM': self.ITEM_SITUACAO_TRAMITE_REGISTRO,
            'FUNDACAO_TAB': self.COD_TABELA_FUNDACOES,
            "DT_REGISTRO": date.today()
        }
        consts.update(super_consts)
        return consts

    @as_transaction
    def perform_work(self, dataset, commit=True):
        """
        [1] Insere em projetos - criar_projeto
        [2] Insere arquivos - __cadastrar_arquivos_basicos
        [3] Insere em PARTICIPANTES_PROJETOS - Coordenador - __cadastra_coordenador_como_participante
        [4] Insere em ORGAOS_PROJETOS - __cadastra_orgao_responsavel
        [5]
        :param dataset:
        :param commit:
        """
        dataset.update(self.constants)

        # 2
        if dataset['TEM_APOIO_FINANCEIRO']:
            # CADASTRA ORGAO - AGENCIA DE FOMENTO - FINANCIADOR
            # CADASTRA ARQUIVO - TERMO DE OUTORGA
            pass
        else:
            # TODO CADASTRA UM ARQUIVO - ATA DO DEPARTAMENTO
            pass


class RegistroProjetoPesquisa(BaseSIEProcedure):
    @as_transaction
    def perform_work(self, dataset, commit=True):
        """
        [1] Chama CriarDocumentoProjetoPesquisa
        [2] atualiza projeto

        :param dataset:
        :param commit:
        :return:
        """
        # 1
        documento_procedure = CriarDocumentoProjetoPesquisa(self.datasource)
        documento_procedure.perform_work(dataset, commit=False)

        # 2
        table = self.datasource.PROJETOS
        self.datasource(table.ID_PROJETO == dataset['ID_PROJETO']).update(**self._dataset_for_table(table, dataset))
