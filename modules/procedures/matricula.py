# coding=utf-8
from datetime import date, datetime
from .base import BaseSIEProcedure
from .exceptions import ProcedureDatasetException, DateConversionException, InvalidDatasetException
from gluon.contrib.pypyodbc import DataError
from br_documents import CPF


class MatricularAlunos(BaseSIEProcedure):
    required_fields = {
        "COD_CURSO": "str",
        "NOME_PESSOA": "str",
        "SEXO": "str",
        "NOME_PAI": "str",
        "NOME_MAE": "str",
        "NACIONALIDADE": "str",
        "DESCR_MAIL": "str",
        "RG": "str",
        "RG_EXPEDICAO": "str",
        "CPF": "str",
        "DT_NASCIMENTO": "date"
    }

    consts = {
        'IND_SEM_CEP': 'N',  # TODO não faço ideia do que seja isso, mas é campo obrigatório
        'TIPO_ORIGEM_TAB': 141,  # Tipo Origem do Endereço
        'TIPO_ORIGEM_ITEM': 11,  # Aluno
        'TIPO_ENDERECO': 'R',  # Residencial
        'TIPO_END_TAB': 240,  # Tipos de endereços
        'TIPO_END_ITEM': 1,  # Residencial
        'NATUREZA_JURIDICA': 'F',  # Pessoa física
        'PERIODO_INGRE_TAB': 608,  # Períodos base do Sistema Acadêmico
        'PER_INGR_INST_TAB': 608,  # Deve ser igual ao PERIODO_INGRE
        'FORMA_INGRE_TAB': 612,  # Forma de ingresso do aluno
        'FORMA_EVASAO_TAB': 613,  # Forma de evasão do aluno
        'FORMA_EVASAO_ITEM': 1,  # Sem evasao
        'DIREITO_MATR_TAB': 818,  # Direito a matrícula
        'DIREITO_MATR_ITEM': 1,  # Tem direito
        'IND_FORMANDO': 'N',  # Não formado
        "COD_OPERADOR": 1,  # admin
        "CONCORRENCIA": 999,
        "DT_ALTERACAO": str(date.today()),
        "HR_ALTERACAO": datetime.now().time().strftime("%H:%M:%S"),
        "ANO_INGRESSO": 2013,  # todo Remover. Deve ser passado no CSV
        "semestre": 1  # todo Remover. Deve ser passado no CSV
    }

    documentos = {1: 'CPF', 2: 'RG'}
    PERIODO_INGRE_ITEM = {1: 201, 2: 202}

    def _pessoa_for_cpf(self, cpf):
        result = self.datasource.executesql(
            "SELECT ID_PESSOA FROM DBSM.DOC_PESSOAS WHERE REPLACE(REPLACE(NUMERO_DOCUMENTO, '.',''), '-','') = '" + cpf + "' FETCH FIRST 1 ROWS ONLY")
        if result:
            return result[0][0]

    def _existe_documento(self, ID_TDOC_PESSOA, ID_PESSOA):
        """
        :type ID_TDOC_PESSOA: int
        :type ID_PESSOA: int
        """
        return self.datasource((self.datasource.DOC_PESSOAS.ID_PESSOA == ID_PESSOA)
                               & (self.datasource.DOC_PESSOAS.ID_TDOC_PESSOA == ID_TDOC_PESSOA)).select()

    def _criar_endereco(self, dataset):
        """
        :type dataset: dict
        """

        try:
            return self.datasource.ENDERECOS.insert(
                ID_ORIGEM=dataset['ID_ALUNO'],
                IND_CORRESP='S',
                **self._dataset_for_table(self.datasource.ENDERECOS, dataset)
            )
        except Exception as e:
            # TODO por algum motivo o driver da um erro louco no primeiro item da queue
            pass

    def _remover_ind_correspondencia(self, TIPO_ORIGEM_ITEM, ID_ALUNO):
        """
        :type ID_TDOC_PESSOA: int
        :type ID_PESSOA: int
        """
        return self.datasource((self.datasource.ENDERECOS.ID_ORIGEM == ID_ALUNO)
                               & (self.datasource.ENDERECOS.TIPO_ORIGEM_ITEM == TIPO_ORIGEM_ITEM)).update(
            IND_CORRESP='N')

    def _is_aluno_matriculado(self, ID_ALUNO, ID_VERSAO_CURSO):
        # todo Deveria estar consultando uma View
        FORMA_EVASAO_ITEM = 1

        return self.datasource(
            (self.datasource.CURSOS_ALUNOS.ID_ALUNO == ID_ALUNO)
            & (self.datasource.CURSOS_ALUNOS.ID_VERSAO_CURSO == ID_VERSAO_CURSO)
            & (self.datasource.CURSOS_ALUNOS.FORMA_EVASAO_ITEM == FORMA_EVASAO_ITEM)).select()

    def _versao_corrente_curso(self, COD_CURSO):
        """
        :rtype : dict
        """
        SITUACAO_VERSAO = 'C'  # versão corrente

        return self.datasource(
            (self.datasource.CURSOS.COD_CURSO == COD_CURSO)
            & (self.datasource.CURSOS.ID_CURSO == self.datasource.VERSOES_CURSOS.ID_CURSO)
            & (self.datasource.VERSOES_CURSOS.SITUACAO_VERSAO == SITUACAO_VERSAO)
        ).select(self.datasource.VERSOES_CURSOS.ID_VERSAO_CURSO).first()

    def _count_matriculados(self, ANO_INGRESSO, semestre, ID_VERSAO_CURSO):
        return self.datasource((self.datasource.CURSOS_ALUNOS.ANO_INGRESSO == ANO_INGRESSO)
                               & (self.datasource.CURSOS_ALUNOS.PERIODO_INGRE_ITEM == self.PERIODO_INGRE_ITEM[semestre])
                               & (self.datasource.CURSOS_ALUNOS.ID_VERSAO_CURSO == ID_VERSAO_CURSO)).count()

    def _novo_matricula_aluno(self, dataset):
        """
        Uma matrícula é formada pela concatenação do ano, semestre, código do curso e um número `sequencial` único.
        Para gerar uma nova matrícula única, toma-se como pré suposto que a nova posição válida para o `sequencial` é
        equivalente a quantidade total de matriculados em um curso, neste ano e semestre, acrescido de 1. Após gerar,
        verifica-se se o mesmo é único e, se não, repete a verificação sucessivamente com sequencial+1 até que seja
        gerado uma matrícula única.

        :return: Uma string correspondente a um MATR_ALUNO único
        """
        matriculados = self._count_matriculados(dataset['ANO_INGRESSO'], dataset['semestre'], dataset['ID_VERSAO_CURSO'])

        _pad = lambda a: "%0*d" % (3, int(a))  # Completa com 0 a esquerda se int(a) < 3

        def _cod_curso(cod):
            """
            Cursos presenciais e de gradução possuem COD_CURSO numérico e, para cursos com menos de 3 dígitos, é
            preciso realizar padding a esquerda. Cursos de pós-graduação funcionam de forma diferente e o código
            costuma ser uma string

            :rtype : str
            :param cod: atributo COD_CURSO de uma entrada na tabela CURSOS
            :return: COD_CURSO formatado
            """
            try:
                return _pad(cod)
            except ValueError:
                return cod

        def _matricula_existe(MATR_ALUNO):
            """
            :param MATR_ALUNO: str correspondente ao campo MATR_ALUNO da tabela CURSOS_ALUNOS
            :return: gluon.dal.Row ou None caso não exista
            """
            return self.datasource(self.datasource.CURSOS_ALUNOS.MATR_ALUNO == MATR_ALUNO).select()

        def _MATR_ALUNO(dataset, sequencial):
            return "%s%s%s%s" % (
            dataset['ANO_INGRESSO'], dataset['semestre'], _cod_curso(dataset['COD_CURSO']), _pad(sequencial))

        MATR_ALUNO = _MATR_ALUNO(dataset, matriculados + 1)

        while _matricula_existe(MATR_ALUNO):
            matriculados += 1
            MATR_ALUNO = _MATR_ALUNO(dataset, matriculados)

        return MATR_ALUNO

    def _criar_curso_aluno(self, dataset):
        return self.datasource.CURSOS_ALUNOS.insert(
            PERIODO_INGRE_ITEM=self.PERIODO_INGRE_ITEM[dataset['semestre']],
            PER_INGR_INST_ITEM=self.PERIODO_INGRE_ITEM[dataset['semestre']],
            **self._dataset_for_table(self.datasource.CURSOS_ALUNOS, dataset)
        )

    def _get_nacionalidade_item(self, nacionalidade):
        """
        :type nacionalidade: str
        :return: ITEM_TABELA correspondente da TAB_ESTRUTURADA
        :raises KeyError: Caso uma descrição compatível não seja encontrada

        """
        nacionalidade = self.datasource(
            (self.datasource.TAB_ESTRUTURADA.COD_TABELA == 163)
            & (self.datasource.TAB_ESTRUTURADA.DESCRICAO.contains(nacionalidade))
        ).select(self.datasource.TAB_ESTRUTURADA.ITEM_TABELA)

        return nacionalidade[0]['ITEM_TABELA']

    def _documento_com_mascara(self, NUMERO_DOCUMENTO, ID_TDOC_PESSOAS):
        """

        :param NUMERO_DOCUMENTO: CPF ou RH
        :param ID_TDOC_PESSOAS: enum documentos
        :return:
        """
        if ID_TDOC_PESSOAS == 1:
            return CPF(NUMERO_DOCUMENTO).formated
        return NUMERO_DOCUMENTO

    def perform_work(self, dataset):
        """
        Esta procedure realiza uma sequência de inserções referentes a matrícula de um aluno. O conceito de ALUNO no SIE
        é uma PESSOA associada a uma versão corrente CURSO em VERSOES_CURSOS, através da tabela CURSOS_ALUNOS.

        * [1] Insere se não existir, uma nova entra em PESSOAS
        * [2] Insere se não existir, novas entradas em DOC_PESSOAS para CPF e RG do aluno
        * [3] Insere se não existir, um nova entrada em ALUNOS
        * [4] Insere ou atualiza, nova entrada em ENDERECO para logradouro, email e telefones
        * [5] Insere uma nova entrada na tabela CURSOS_ALUNOS, que representa uma nova matrícula de ALUNO em VERSOES_CURSOS

        :rtype : dict
        :type dataset: dict
        :param dataset:
        """

        # todo Não deveria ser necessário reconectar, mas após o final de uma requisição, o web2py fecha todas as conexoes
        if not self.datasource._adapter.connection:
            self.datasource._adapter.reconnect()

        dataset.update(self.consts)

        try:
            dataset.update({k: self.convert_date_format(v) for k, v in dataset.iteritems()
                            if self.required_fields.get(k, None) == 'date'})
        except ValueError as e:
            raise DateConversionException(dataset, e)

        try:
            dataset.update(NACIONALIDADE_ITEM=self._get_nacionalidade_item(dataset['NACIONALIDADE']))
        except KeyError as e:
            raise InvalidDatasetException(dataset, e)

        try:
            # 1
            pessoa = self._pessoa_for_cpf(dataset['CPF'])
            if pessoa:
                dataset.update({'ID_PESSOA': pessoa})
            else:
                self.datasource.PESSOAS.insert(**self._dataset_for_table(self.datasource.PESSOAS, dataset))
            # 2
            for ID_TDOC_PESSOA, dataset_key in self.documentos.iteritems():
                if not self._existe_documento(ID_TDOC_PESSOA, dataset['ID_PESSOA']):
                    self.datasource.DOC_PESSOAS.insert(
                        ID_TDOC_PESSOA=ID_TDOC_PESSOA,
                        NUMERO_DOCUMENTO=self._documento_com_mascara(dataset[dataset_key], ID_TDOC_PESSOA),
                        **self._dataset_for_table(self.datasource.DOC_PESSOAS, dataset)
                    )
            # 3
            aluno = self.datasource(self.datasource.ALUNOS.ID_PESSOA == dataset['ID_PESSOA']).select().first()
            if aluno:
                dataset.update(ID_ALUNO=aluno.ID_ALUNO)
            else:
                self.datasource.ALUNOS.insert(**self._dataset_for_table(self.datasource.ALUNOS, dataset))
            # 4
            self._remover_ind_correspondencia(dataset['TIPO_ORIGEM_ITEM'], dataset['ID_ALUNO'])
            self._criar_endereco(dataset)
            # 5
            dataset.update(self._versao_corrente_curso(dataset['COD_CURSO']))

            if not self._is_aluno_matriculado(dataset['ID_ALUNO'], dataset['ID_VERSAO_CURSO']):
                dataset.update(MATR_ALUNO=self._novo_matricula_aluno(dataset))
                self._criar_curso_aluno(dataset)
            self.datasource.commit()
            return dataset
        except Exception as e:
            self.datasource.rollback()
            raise ProcedureDatasetException(dataset, e)
        except DataError as e:
            pass
