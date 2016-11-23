# coding=utf-8
from procedures.base import BaseSIEProcedure, as_transaction


class CriarEndereco(BaseSIEProcedure):
    """
    Cria endereço(s) para pessoas físicas a partir de um CPF. Busca os
    endereços da pessoa e, caso existam, remove os respectivos IND_CORRESP;
    Atende aos casos de pessoa aluno, servidor e aluno que é servidor, criando
    1 ou 2 endereços para os respectivos tipo_origem_item.
    Aluno = ID_ALUNO
    Funcionario, Entidade Externa = ID_PESSOA

    """
    methods = ("POST",)

    COD_TABELA_TIPO_ENDERECO = 240
    COD_TABELA_TIPO_ORIGEM = 141
    RESIDENCIAL = 'R'
    RESIDENCIAL_ITEM = 1
    SEM_CEP = 'N'
    TIPO_ORIGEM_ITEM_ALUNO = 11
    TIPO_ORIGEM_ITEM_FUNCIONARIO = 2

    origens = {
        'id_aluno': TIPO_ORIGEM_ITEM_ALUNO,
        'id_funcionario': TIPO_ORIGEM_ITEM_FUNCIONARIO
    }

    @property
    def _table(self):
        return self.datasource.enderecos

    @property
    def schema(self):
        super_required = super(CriarEndereco, self).schema
        required = {
            'cpf': 'string',
            'descr_rua': 'string',
            'descr_numero': 'string',
            'descr_complemento': 'string',
            'descr_bairro': 'string',
            'descr_municipio': 'string',
            'descr_estado': 'string',
            'descr_pais': 'string',
            'descr_cep': 'string',
            'descr_mail': 'string'
        }
        required.update(super_required)

        return required

    @property
    def constants(self):
        super_consts = super(CriarEndereco, self).constants
        consts = {
            'ind_corresp': 'S',
            'ind_sem_cep': self.SEM_CEP,
            'tipo_end_tab': self.COD_TABELA_TIPO_ENDERECO,
            'tipo_origem_tab': self.COD_TABELA_TIPO_ORIGEM,
            'tipo_end_item': self.RESIDENCIAL_ITEM,
            'tipo_endereco': self.RESIDENCIAL
        }
        consts.update(super_consts)
        return consts

    def _id_pessoa_de_cpf(self, cpf):
        """
        Dado um cpf, a função retorna o id_pessoa

        :type cpf: str
        :rtype: long
        """
        # todo: a view a ser usada não deveria ser essa
        view = self.datasource.v_projetos_pessoas
        pessoa = self.datasource(view.cpf == cpf).select(view.id_pessoa)

        return pessoa.first().id_pessoa

    def __criar_enderecos(self, dataset, tipos_origem):
        table = self.datasource.enderecos
        for origem in tipos_origem:
            yield table.insert(tipo_origem_item=origem,
                               id_origem=dataset['id_pessoa'],
                               **self._dataset_for_table(table, dataset))

    def __buscar_enderecos(self, dataset):
        view = self.datasource.v_pessoas_enderecos
        condition = (view.id_pessoa == dataset['id_pessoa'])
        endereco = self.datasource(condition).select().first()

        return endereco

    def __remover_ind_corresp(self, ids):
        """
        :param ids: Uma lista de inteiros correspondente a id_endereco
        :type ids: Iterable
        """
        table = self.datasource.enderecos
        for id in ids:
            self.datasource(table.id_endereco == id).update(ind_corresp='N')

    def __ids_de_endereco(self, endereco):
        """
        :param endereco: Um objecto row da view v_pessoas_enderecos
        :type endereco: Row
        """
        for key in self.origens:
            if endereco[key]:
                yield endereco[key]

    def __origens_para_endereco(self, endereco):
        """
        Dada uma Row de v_pessoas_enderecos, o método retorna os respectivos
         tipo_origem_item válidos para a pessoa

        :param endereco: Um objecto row da view v_pessoas_enderecos
        :type endereco: Row
        """
        for key, tipo_origem in self.origens.iteritems():
            if endereco[key]:
                yield tipo_origem

    @as_transaction
    def perform_work(self, dataset, commit):
        dataset.update(self.constants)
        dataset['id_pessoa'] = self._id_pessoa_de_cpf(dataset['cpf'])

        endereco = self.__buscar_enderecos(dataset)
        tipos_origem = self.__origens_para_endereco(endereco)

        self.__remover_ind_corresp(ids=self.__ids_de_endereco(endereco))
        dataset['id_endereco'] = tuple(self.__criar_enderecos(dataset,
                                                              tipos_origem))

        return dataset
