# coding=utf-8
from datetime import date

from procedures.base import BaseSIEProcedure, as_transaction
from procedures.exceptions import ProcedureException


__all__ = ("CriarFuncionario", "CriarFuncionarioProfExterno")


class CriarFuncionario(BaseSIEProcedure):
    ESTADO_CIVIL_TAB = 162
    NACIONALIDADE_TAB = 163
    DEFICIENCIA_TAB = 229
    PAIS_ORIGEM_TAB = 204
    ESCOLARIDADE_TAB = 168
    ETNIA_TAB = 509

    @property
    def required_fields(self):
        super_required = super(CriarFuncionario, self).required_fields
        required = {
            # "nome_funcionario": "string",
            "sexo": "string",
            "id_naturalidade": "int",
            "dt_nascimento": "date",
            "id_pessoa": "int"
        }
        required.update(super_required)

        return required

    @property
    def constants(self):
        super_consts = super(CriarFuncionario, self).constants
        consts = {
            "dt_admissao_sp": date.today(),
            "estado_civil_tab": self.ESTADO_CIVIL_TAB,
            "nacionalidade_tab": self.NACIONALIDADE_TAB,
            "deficiencia_tab": self.DEFICIENCIA_TAB,
            "pais_origem_tab": self.PAIS_ORIGEM_TAB,
            "escolaridade_tab": self.ESCOLARIDADE_TAB,
            "etnia_tab": self.ETNIA_TAB
        }
        consts.update(super_consts)
        return consts

    def get_pessoa(self, id_pessoa):
        table = self.datasource.pessoas
        return self.datasource(table.id_pessoa == id_pessoa).select().first()

    def criar_funcionario(self, dataset):
        table = self.datasource.funcionarios
        return table.insert(**self._dataset_for_table(table, dataset))

    @as_transaction
    def perform_work(self, dataset, commit):
        dataset.update(self.constants)

        pessoa = self.get_pessoa(dataset['id_pessoa'])
        dataset['nome_funcionario'] = pessoa['nome_pessoa']

        funcionario = self.criar_funcionario(dataset)
        dataset.update(funcionario)

        return dataset


class CriarFuncionarioProfExterno(CriarFuncionario):
    FORMA_INGRESSO_TAB = 161
    FORMA_INGRESSO_CONTRATACAO_DIRETA = 11

    REGIME_JURIDICO_TAB = 165
    REGIME_JURIDICO_NATUREZA_ESPECIAL = 3

    SITUACAO_TAB = 166
    SITUACAO_ATIVO_PROF_EXTERNO = 100
    SITUACAO_INATIVO_PROF_EXTERNO = 101

    JORNADA_TAB = 167
    JORNADA_NAO_INFORMADA = 100

    CATEGORIA_TAB = 172
    CATEGORIA_TRABALHADOR_AVULSO = 2

    TIPO_CONTRATO_TAB = 303
    TIPO_CONTRATO_HORISTA = 2

    TIPO_ADMISSAO_TAB = 304
    TIPO_ADMISSAO_PRIMEIRO_EMPREGO = 1
    TIPO_ADMISSAO_REEMPREGO = 2

    TIPO_VINCULO_TAB = 316
    TIPO_VINCULO_TRAB_URBANO_PESSOA_FISICA = 2

    TIPO_DESLIGAMENTO_TAB = 305
    TIPO_DESLIGAMENTO_SEM_DESLIGAMENTO = 1101
    TIPO_DESLIGAMENTO_CONTRATO_TEMPORARIO = 1105
    TIPO_DESLIGAMENTO_RESCISAO_CONTRATO = 1205
    TIPO_DESLIGAMENTO_ERROR_DE_CADASTRO = 1208
    TIPO_DESLIGAMENTO_FALTA_DE_RECADASTRAMENTO = 1222

    # todo: achar ID_CARGO em CARGOS_RH
    ID_CARGO_PROF_EXTERNO = NotImplemented

    DATAS_INICIO = ('dt_admissao_cargo',
                    'dt_admissao_inst',
                    'dt_nomeacao',
                    'dt_posse')

    # Gambi Alex Síntese
    MASCARA = '99'
    MIN_MATR_PROF_EXTERNO = 9900000
    MAX_MATR_PROF_EXTERNO = 9999999

    @property
    def required_fields(self):
        """
        Segundo documento `PROCESSO DE GESTÃO DOS CURSOS DE PÓS-GRADUAÇÃO
        CADASTRAMENTO DE PROFESSORES EXTERNOS`

        Dados do contrato:
        * Solicitar a vigência do contrato
        * Solicitar a unidade responsável
        * Solicitar o papel do docente

        """
        super_required = super(CriarFuncionarioProfExterno, self).required_fields
        required = {
            'id_plano': 'int',
            'id_lot_oficial': 'int',
            'id_lot_exercicio': 'int',
            'dt_inicio': 'date',
            'dt_fim': 'date'
        }
        required.update(super_required)

        return required

    @property
    def constants(self):
        super_consts = super(CriarFuncionarioProfExterno, self).constants
        consts = {
            'formaingresso_tab': self.FORMA_INGRESSO_TAB,
            'formaingresso_item': self.FORMA_INGRESSO_CONTRATACAO_DIRETA,
            'reg_juridico_tab': self.REGIME_JURIDICO_TAB,
            'reg_juridico_item': self.REGIME_JURIDICO_NATUREZA_ESPECIAL,
            'situacao_tab': self.SITUACAO_TAB,
            'situacao_item': self.SITUACAO_ATIVO_PROF_EXTERNO,
            'jornada_trab_tab': self.JORNADA_TAB,
            'jornada_trab_item': self.JORNADA_NAO_INFORMADA,
            'categoria_tab': self.CATEGORIA_TAB,
            'categoria_item': self.CATEGORIA_TRABALHADOR_AVULSO,
            'tipo_contrato_tab': self.TIPO_CONTRATO_TAB,
            'tipo_contrato_item': self.TIPO_CONTRATO_HORISTA,
            'tipo_admissao_tab': self.TIPO_ADMISSAO_TAB,
            'tipo_vinculo_tab': self.TIPO_VINCULO_TAB,
            'tipo_vinculo_item': self.TIPO_VINCULO_TRAB_URBANO_PESSOA_FISICA,
            'tipo_desliga_tab': self.TIPO_DESLIGAMENTO_TAB,
            'tipo_desliga_item': self.TIPO_DESLIGAMENTO_SEM_DESLIGAMENTO,
            'ind_demissionario': 'N',
            'ind_isencao_ir': 'N',
            'ind_suspensao_pgto': 'N',
            'ind_probatorio': 'N',
            'id_cargo': self.ID_CARGO_PROF_EXTERNO
        }
        consts.update(super_consts)
        return consts

    def __proxima_matricula(self):
        """
        Item 5.a da especificação Síntese
        No composto de 7 dígitos, sequencial, iniciado a partir do no 9900000

        :return: Uma nova matrícula
        :rtype: str
        """
        table = self.datasource.contratos_rh
        conditions = ((table.matr_externa > self.MIN_MATR_PROF_EXTERNO) &
                      (table.matr_externa < self.MAX_MATR_PROF_EXTERNO))
        max = table.matr_externa.max()
        matricula = self.datasource(conditions).select(max).first()[max]

        if not matricula:
            return self.MIN_MATR_PROF_EXTERNO

        matricula = str(matricula)
        proximo_n = int(matricula[len(self.MASCARA):]) + 1
        matricula = "99{:05d}".format(proximo_n)

        if not int(matricula) > self.MAX_MATR_PROF_EXTERNO:
            return matricula

        """
        Boa sorte para você do futuro que vai ter que lidar com isso.
        Pelo menos me agradeça por ter tratado esse caso e deixado seu
        trabalho mais fácil. Não me culpe, eu só implementei. :/
        """
        raise ProcedureException("Gambiarra Sintese chegou ao limite.")

    def tipo_admissao_para_pessoa(self, id_pessoa):
        table = self.datasource.funcionarios
        funcionario = self.datasource(table.id_pessoa == id_pessoa).select()

        if funcionario:
            return self.TIPO_ADMISSAO_REEMPREGO

        return self.TIPO_ADMISSAO_PRIMEIRO_EMPREGO

    def gerar_id_cargo_vaga(self, dataset):
        view = self.datasource.v_papeis_docentes


        # todo: `avisar dpg` == enviar alerta ?
        raise NotImplementedError("CONTRATOS_RH.ID_CARGO_VAGA (pegar o primeiro"
                                  " que tenha disponível. Se não houver, "
                                  "informar para que a DPG aumente o no de "
                                  "vagas disponíveis)")

    @as_transaction
    def perform_work(self, dataset, commit):
        try:
            super(CriarFuncionarioProfExterno, self).perform_work(dataset,
                                                                  commit=False)

            dataset['dt_desligamento'] = dataset['dt_fim']

            for dt in self.DATAS_INICIO:
                dataset[dt] = dataset['dt_inicio']

            admissao = self.tipo_admissao_para_pessoa(dataset['id_pessoa'])
            dataset['tipo_admissao_item'] = admissao

            dataset['matr_externa'] = self.__proxima_matricula()
            dataset.update(self.constants)

            raise Exception()
        except Exception as e:
            raise e
