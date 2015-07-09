# coding=utf-8
from applications.api.modules.procedures.base import BaseSIEProcedure


class MatricularAlunos(BaseSIEProcedure):
    required_fields = frozenset(
        [
            "COD_CURSO",
            "DESCR_RUA",
            "NOME_PESSOA",
            "SEXO",
            "NOME_PAI",
            "NOME_MAE",
            "NACIONALIDADE",
            "DESCR_MAIL",
            "RG",
            "RG_EXPEDICAO",
            "CPF",
            "CEP",
            "CIDADE",
            "TELEFONE1",
            "TELEFONE2"
        ]
    )
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
        IND_SEM_CEP = 'N'   # todo não faço ideia do que seja isso, mas é campo obrigatório
        try:
            return self.datasource.ENDERECOS.insert(
                ID_ORIGEM=dataset['ID_ALUNO'],
                IND_SEM_CEP=IND_SEM_CEP,
                FONE_RESIDENCIAL=dataset['TELEFONE1'],
                FONE_CELULAR=dataset['TELEFONE2'],
                IND_CORRESP='S',
                **self._dataset_for_table(self.datasource.ENDERECOS, dataset)
            )
        except Exception as e:
            # todo por algum motivo o driver da um erro louco no primeiro item da queue
            pass

    def _remover_ind_correspondencia(self, TIPO_ORIGEM_ITEM, ID_ALUNO):
        """
        :type ID_TDOC_PESSOA: int
        :type ID_PESSOA: int
        """
        return self.datasource((self.datasource.ENDERECOS.ID_ORIGEM == ID_ALUNO)
                               & (self.datasource.ENDERECOS.TIPO_ORIGEM_ITEM == TIPO_ORIGEM_ITEM)).update(IND_CORRESP='N')

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
        SITUACAO_VERSAO = 'C'   # versão corrente

        return self.datasource(
            (self.datasource.CURSOS.COD_CURSO==COD_CURSO)
            & (self.datasource.CURSOS.ID_CURSO == self.datasource.VERSOES_CURSOS.ID_CURSO)
            & (self.datasource.VERSOES_CURSOS.SITUACAO_VERSAO == SITUACAO_VERSAO)
        ).select(self.datasource.VERSOES_CURSOS.ID_VERSAO_CURSO).first()


    def _novo_numero_matricula(self, dataset):
        pass
        # return "%s%s%s%s" % (ano, semestre, COD_CURSO, str(sequencial))


    def _criar_curso_aluno(self, dataset):
        MATR_ALUNO = gerarNumeroMatricula(matricula)
        PERIODO_INGRE_TAB = 608
        FORMA_INGRE_TAB = 612  #Forma de ingresso
        FORMA_INGRE_ITEM = str(FORMA_INGRE_ITEM)  #Recebe como parâmetro da aplicação
        FORMA_EVASAO_TAB = 613  #Forma de evasão
        FORMA_EVASAO_ITEM = 1  #1 = sem evasao
        DIREITO_MATR_TAB = 818  # Direito a matrícula
        DIREITO_MATR_ITEM = 1  # Tem direito
        IND_FORMANDO = 'N'  # Não formado


    def perform_work(self, dataset):
        """
        Esta procedure realiza uma sequência de inserções referentes a matrícula de um aluno. O conceito de ALUNO no SIE
        é uma PESSOA associada a uma versão corrente CURSO em VERSOES_CURSOS, através da tabela CURSOS_ALUNOS.

        * [1] Insere se não existir, uma nova entra em PESSOAS
        * [2] Insere se não existir, novas entradas em DOC_PESSOAS para CPF e RG do aluno
        * [3] Insere se não existir, um nova entrada em ALUNOS
        * [4] Insere ou atualiza, nova entrada em ENDERECO para logradouro, email e telefones
        * [5] Insere uma nova entrada na tabela CURSOS_ALUNOS, que representa uma nova matrícula de ALUNO em VERSOES_CURSOS

        :type dataset: dict
        :param dataset:
        """
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
                    NUMERO_DOCUMENTO=dataset[dataset_key],
                    **self._dataset_for_table(self.datasource.DOC_PESSOAS, dataset)
                )

        # 3
        aluno = self.datasource(self.datasource.ALUNOS.ID_PESSOA == dataset['ID_PESSOA']).select().first()
        if aluno:
            dataset.update({'ID_ALUNO': aluno.ID_ALUNO})
        else:
            self.datasource.ALUNOS.insert(**self._dataset_for_table(self.datasource.ALUNOS, dataset))

        # 4
        endereco_consts = {
            'TIPO_ORIGEM_TAB': 141,
            'TIPO_ORIGEM_ITEM': 11,  # Aluno
            'TIPO_ENDERECO': 'R',  # Residencial
            'TIPO_END_TAB': 240,
            'TIPO_END_ITEM': 1  # Residencial
        }
        dataset.update(endereco_consts)

        self._remover_ind_correspondencia(dataset['TIPO_ORIGEM_ITEM'], dataset['ID_ALUNO'])
        self._criar_endereco(dataset)

        # 5
        curso_corrente = self._versao_corrente_curso(dataset['COD_CURSO'])
        dataset.update(curso_corrente)

        if not self._is_aluno_matriculado(dataset['ID_ALUNO'], dataset['ID_VERSAO_CURSO']):
            self._criar_curso_aluno(dataset)

        # self.datasource.comm
