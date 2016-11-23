# coding=utf-8
import json

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
    def schema(self):
        super_schema = super(InscricaoCandidatoPosGraduacao, self).schema
        with open('./schema.json') as fp:
            schema = json.load(fp)
        schema['properties'].update(super_schema['properties'])
        schema['required'] += super_schema['required']

        return schema

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
        schema = self.schema
        self._inserir_info_complementares(dataset)
        self._inserir_arquivo_projeto(dataset)

        return dataset


class BaseSchema(object):
    pass

class DatasetSchema(BaseSchema):
    pass


class Mock(object):
    def __getattr__(self, item):
        return Mock()

    def __getitem__(self, item):
        return Mock()

    def __call__(self, *args, **kwargs):
        return Mock()


procedure = InscricaoCandidatoPosGraduacao(Mock())
procedure.perform_work({}, commit=False)