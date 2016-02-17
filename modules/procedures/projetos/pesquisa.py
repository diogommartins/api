# coding=utf-8
from datetime import date
from procedures.documento import CriarDocumentoProjetoPesquisa
from procedures.base import BaseSIEProcedure, as_transaction
from procedures.exceptions import InvalidDatasetException
from .base import CadastrarProjeto
import gambiarras


class CriarProjetoPesquisa(CadastrarProjeto):
    __post_commit_functions = []

    COD_TABELA_FUNDACOES = 6025
    COD_TABELA_FUNCOES_ORGAOS = 6006
    COD_TABELA_FUNCOES_PROJ = 6003
    COD_TABELA_TITULACAO = 168
    COD_TABELA_TIPO_ARQUIVO = 6005
    COD_TABELA_TIPO_EVENTO = 6028
    COD_TABELA_TIPO_PUBLICO_ALVO = 6002
    COD_TABELA_AVALIACAO_PROJETOS_INSTITUICAO = 6010
    COD_TABELA_SITUACAO = 6011

    COD_SITUACAO_ATIVO = "A"

    ITEM_TITULACAO_INDEFINIDA = 99
    ITEM_TIPO_EVENTO_NAO_SE_APLICA = 1
    ITEM_TIPO_ARQUIVO_PROJETO = 1
    ITEM_TIPO_ARQUIVO_ATA_DEPARTAMENTO = 5
    ITEM_TIPO_ARQUIVO_TERMO_OUTORGA = 19
    ITEM_TIPO_PUBLICO_3_GRAU = 8
    ITEM_AVALIACAO_PROJETOS_INSTITUICAO_NAO_AVALIADO = 1
    ITEM_CLASSIFICACAO_PROJETO_PESQUISA = 39718

    ITEM_SITUACAO_TRAMITE_REGISTRO = 8

    ITEM_FUNCOES_ORGAOS_AGENCIA_FOMENTO = 4
    ITEM_FUNCOES_PROJ_COORDENADOR = 1
    ITEM_FUNCOES_ORGAOS_RESPONSAVEL = 5

    SITUACAO_ATIVO = 'A'
    ACESSO_PARTICIPANTES_APENAS_COORDENADOR = 'N'
    NAO_PAGA_BOLSA = 'N'

    @property
    def constants(self):
        super_consts = super(CriarDocumentoProjetoPesquisa, self).constants
        consts = {
            'EVENTO_TAB': self.COD_TABELA_TIPO_EVENTO,
            'EVENTO_ITEM': self.ITEM_TIPO_EVENTO_NAO_SE_APLICA,
            'TIPO_PUBLICO_TAB': self.COD_TABELA_TIPO_PUBLICO_ALVO,
            'TIPO_PUBLICO_ITEM': self.ITEM_TIPO_PUBLICO_3_GRAU,
            'ACESSO_PARTICIP': self.ACESSO_PARTICIPANTES_APENAS_COORDENADOR,
            'PAGA_BOLSA': self.NAO_PAGA_BOLSA,
            'AVALIACAO_TAB': self.COD_TABELA_AVALIACAO_PROJETOS_INSTITUICAO,
            'AVALIACAO_ITEM': self.ITEM_AVALIACAO_PROJETOS_INSTITUICAO_NAO_AVALIADO,
            'ID_CLASSIFICACAO': self.ITEM_CLASSIFICACAO_PROJETO_PESQUISA,
            'SITUACAO_TAB': self.COD_TABELA_SITUACAO,
            'SITUACAO_ITEM': self.ITEM_SITUACAO_TRAMITE_REGISTRO,
            'FUNDACAO_TAB': self.COD_TABELA_FUNDACOES,
            'DT_REGISTRO': date.today()
        }
        consts.update(super_consts)
        return consts

    @property
    def required_fields(self):
        super_required = super(CriarProjetoPesquisa, self).required_fields
        required = {
            'CARGA_HORARIA': 'int',
            'ID_CONTRATO_RH': 'int',
            'ID_PESSOA': 'int',
            'ID_UNIDADE': 'int',    # coordenador ID_LOT_OFICIAL
            'DT_INICIAL': 'date',
            'DT_FINAL': 'date',
            'DESCR_MAIL': 'str'
        }
        required.update(super_required)
        return required

    def __criar_projeto(self, dataset):
        table = self.datasource.PROJETOS
        return table.insert(**self._dataset_for_table(table, dataset))

    def __cadastrar_coordenador_como_participante(self, dataset):
        table = self.datasource.PARTICIPANTES_PROJ

        table.insert(
                CH_SUGERIDA=dataset['CARGA_HORARIA'],
                FUNCAO_ITEM=self.ITEM_FUNCOES_PROJ_COORDENADOR,
                FUNCAO_TAB=self.COD_TABELA_FUNCOES_PROJ,
                SITUACAO=self.COD_SITUACAO_ATIVO,
                TITULACAO_ITEM=self.ITEM_TITULACAO_INDEFINIDA,
                TITULACAO_TAB=self.COD_TABELA_TITULACAO,
                **self._dataset_for_table(table, dataset)
        )

    def __cadastrar_orgao(self, dataset, item):
        table = self.datasource.ORGAOS_PROJETOS

        table.insert(
                FUNCAO_ORG_ITEM=self.ITEM_FUNCOES_ORGAOS_RESPONSAVEL,
                FUNCAO_ORG_TAB=self.COD_TABELA_FUNCOES_ORGAOS,
                SITUACAO=self.COD_SITUACAO_ATIVO,
                **self._dataset_for_table(table, dataset)
        )

    def __cadastrar_orgao_responsavel(self, dataset):
        self.__cadastrar_orgao(dataset, self.ITEM_FUNCOES_ORGAOS_RESPONSAVEL)

    def __cadastrar_orgao_agencia_fomento(self, dataset):
        self.__cadastrar_orgao(dataset, self.ITEM_FUNCOES_ORGAOS_AGENCIA_FOMENTO)

    def __salvar_arquivo(self, dataset, prefixo, item):
        """
        :rtype : dict
        """
        table = self.datasource.ARQUIVOS_PROJ
        try:
            stmt = self.datasource.ARQUIVOS_PROJ._insert(
                    CONTEUDO_ARQUIVO=dataset[prefixo + 'CONTEUDO_ARQUIVO'],
                    DT_INCLUSAO=dataset['DT_INICIAL'],
                    NOME_ARQUIVO=dataset[prefixo + 'NOME_ARQUIVO'],
                    TIPO_ARQUIVO_ITEM=item,
                    TIPO_ARQUIVO_TAB=self.COD_TABELA_TIPO_ARQUIVO,
                    **self._dataset_for_table(table, dataset)
            )
        except KeyError as e:
            raise InvalidDatasetException(dataset, e)

        # Acredita... Nada disso deveria existir. GAMBIARRA! X_X ! Não toque.
        blob_values = (dataset[prefixo + 'CONTEUDO_ARQUIVO'],)
        self.datasource.executesql(stmt, blob_values)

        insert_by_gambi = lambda: gambiarras.insert_blob(dataset['ID_ARQUIVO_PROJ'],
                                                         zip(('CONTEUDO_ARQUIVO',), blob_values),
                                                         table,
                                                         table._primarykey[0])

        self.__post_commit_functions.append(insert_by_gambi)

    @as_transaction
    def perform_work(self, dataset, commit=True):
        """
        [1] Insere em projetos - criar_projeto
        [2] Insere arquivos - __cadastrar_arquivos_basicos
        [3] Insere em PARTICIPANTES_PROJETOS - Coordenador - __cadastra_coordenador_como_participante
        [4] Insere em ORGAOS_PROJETOS - __cadastra_orgao_responsavel
        [5] Insere em arquivos - salva arquivo de projeto

        """
        dataset.update(self.constants)

        self.__criar_projeto(dataset)

        if dataset.get('TEM_APOIO_FINANCEIRO', False):
            if 'VL_CONTRIBUICAO' not in dataset:
                raise InvalidDatasetException(dataset, KeyError("VL_CONTRIBUICAO deve estar presente em um dataset com TEM_APOIO_FINANCEIRO"))

            self.__cadastrar_orgao_agencia_fomento(dataset)

            self.__salvar_arquivo(dataset, 'OUTORGA_', self.ITEM_TIPO_ARQUIVO_TERMO_OUTORGA)
        else:
            self.__salvar_arquivo(dataset, 'DEPARTAMENTO_', self.ITEM_TIPO_ARQUIVO_ATA_DEPARTAMENTO)

        self.__cadastrar_coordenador_como_participante(dataset)

        self.__cadastrar_orgao_responsavel(dataset)

        self.__salvar_arquivo(dataset, 'PROJETO_', self.ITEM_TIPO_ARQUIVO_PROJETO)

    def on_commit(self):
        for func in list(self.__post_commit_functions):
            func()
            self.__post_commit_functions.remove(func)


class RegistroProjetoPesquisa(BaseSIEProcedure):
    def __atualizar_projeto(self, dataset):
        table = self.datasource.PROJETOS
        self.datasource(table.ID_PROJETO == dataset['ID_PROJETO']).update(**self._dataset_for_table(table, dataset))

    def __criar_documento(self, dataset):
        documento_procedure = CriarDocumentoProjetoPesquisa(self.datasource)
        documento_procedure.perform_work(dataset, commit=False)

    @as_transaction
    def perform_work(self, dataset, commit=True):
        self.__criar_documento(dataset)

        self.__atualizar_projeto(dataset)