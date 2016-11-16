# coding=utf-8
from procedures.base import BaseSIEProcedure, as_transaction
from procedures.exceptions import InvalidDatasetException
from datetime import date


class InscricaoCandidatoPosGraduacao(BaseSIEProcedure):
    COD_TABELA_NACIONALIDADE = 6021
    COD_TABELA_ESTADO_CIVIL = 162
    COD_TABELA_ETNIA = 509
    COD_TABELA_DEFICIENCIA = 229
    COD_TABELA_UF = 206
    COD_TABELA_TIPO_ARQUIVO = 6099  # arquivos_incricoes
    ID_NACIONALIDADE_BRASILEIRO = 1  # nato ou naturalizado
    TIPO_ARQUIVO_PROJETO = 1

    @property
    def required_fields(self):
        super_required = super(InscricaoCandidatoPosGraduacao,
                               self).required_fields
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
            'cor_item': 'int',
            'uf_item': 'int',
            'id_naturalidade': 'int',
            # candidatos_comp
            'ano_conclusao': 'int',
            'instituicao_conclusao': 'string',
            'foto': 'blob',
            # arquivos_inscricoes
            'conteudo_arquivo': 'blob',
            'nome_arquivo': 'string',
            'ind_concluido': 'boolean',
            'ind_declara_veracidade': 'boolean'

        }
        required.update(super_required)

        return required

    def schema(self):
        schema = {
            "type": "object",
            "properties": {
                # CANDIDATOS
                "cpf": {"type": "string"},
                "id_concurso": {"type": "integer"},
                "id_conc_edicao": {"type": "integer"},
                "id_opcao": {"type": "integer"},
                "id_cota_edicao": {"type": "integer"},
                "nome_pessoa": {"type": "string"},
                "dt_nascimento": {"type": "date"},
                "estado_civil_item": {"type": "integer"},
                "sexo": {"type": "string"},
                "nome_pai": {"type": "string"},
                "nome_mae": {"type": "string"},
                "nacionalidade_item": {"type": "integer"},
                "deficiencia_item": {"type": "integer"},
                "tipo_sanguineo": {"type": "string"},
                "fator_rh": {"type": "string"},
                "cor_item": {"type": "integer"},
                "uf_item": {"type": "integer"},
                "id_naturalidade": {"type": "integer"},
                "ano_conclusao": {"type": "integer"},
                "instituicao_conclusao": {"type": "string"},
                "foto": {"type": "blob"},
                "conteudo_arquivo": {"type": "blob"},
                "nome_arquivo": {"type": "string"},
                "ind_concluido": {"type": "boolean"},
                "ind_declara_veracidade": {"type": "boolean"},
                "link_lattes": {"type": "string"}
            },
            "required": ["cpf", "id_concurso", "id_conc_edicao", "id_opcao",
                         "id_cota_edicao", "nome_pessoa", "dt_nascimento",
                         "estado_civil_item", "sexo", "nome_pai", "nome_mae",
                         "nacionalidade_item", "deficiencia_item",
                         "tipo_sanguineo", "fator_rh", "cor_item", "uf_item",
                         "id_naturalidade", "ano_conclusao",
                         "instituicao_conclusao", "foto", "conteudo_arquivo",
                         "nome_arquivo", "ind_concluido",
                         "ind_declara_veracidade"]
        }

    @property
    def constants(self):
        super_consts = super(InscricaoCandidatoPosGraduacao,
                             self).constants
        consts = {
            'estado_civil_tab': self.COD_TABELA_ESTADO_CIVIL,
            'nacionalidade_tab': self.COD_TABELA_NACIONALIDADE,
            'cor_tab': self.COD_TABELA_ETNIA,
            'uf_tab': self.COD_TABELA_UF,
            # candidatos_comp
            'ind_concluido': 'S',
            'ind_declara_veracidade': 'S',
            # arquivos_inscricoes
            'tipo_arquivo_tab': self.COD_TABELA_TIPO_ARQUIVO,
            'tipo_arquivo_item': self.TIPO_ARQUIVO_PROJETO,
            'dt_inclusao': date.today()
        }

        consts.update(super_consts)
        return consts

    def __is_brasileiro(self, dataset):
        return dataset['nacionalidade_item'] == self.ID_NACIONALIDADE_BRASILEIRO

    def on_validate(self, dataset):
        if self.__is_brasileiro(dataset):
            return
        if not dataset['passaporte']:
            raise InvalidDatasetException(dataset,
                                          "'passaporte' é esperado para"
                                          " candidatos estrangeiros")

    def gerar_num_inscricao(self):
        raise NotImplementedError()

    def _inserir_info_complementares(self, dataset):
        pass

    def _inserir_arquivo_projeto(self, dataset):
        pass

    @as_transaction
    def perform_work(self, dataset, commit=False):

        self._inserir_info_complementares(dataset)
        self._inserir_arquivo_projeto(dataset)
        raise NotImplementedError("Precisa ser implementado")

        return dataset
