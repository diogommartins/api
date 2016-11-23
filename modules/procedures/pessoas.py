# coding=utf-8
from procedures.base import BaseSIEProcedure, as_transaction
from procedures.exceptions import InvalidDatasetException
from brazilnum.cpf import format_cpf, validate_cpf


__all__ = ("CriarPessoaFisica",)


class CriarPessoaFisica(BaseSIEProcedure):
    PESSOA_FISICA = 'F'
    ID_TDOCS = {
        'cpf': 1,
        'rg': 2
    }

    @property
    def required_fields(self):
        super_required = super(CriarPessoaFisica, self).required_fields
        required = {
            "cpf": "string",
            "dt_nascimento": "date",
            "nome_pessoa": "string",
            "rg": "string",
            "sexo": "string",
            "naturalidade": "string",
            "nacionalidade": "string"
        }
        required.update(super_required)

        return required

    @property
    def constants(self):
        super_consts = super(CriarPessoaFisica, self).constants
        consts = {
            "natureza_juridica": self.PESSOA_FISICA
        }
        consts.update(super_consts)
        return consts

    def criar_pessoa(self, dataset):
        table = self.datasource.pessoas
        return table.insert(**self._dataset_for_table(table, dataset))

    def criar_documentos(self, dataset):
        table = self.datasource.doc_pessoas

        for doc, id_tdoc_pessoa in self.ID_TDOCS.iteritems():
            doc_pessoa = table.insert(id_tdoc_pessoa=id_tdoc_pessoa,
                                      numero_documento=dataset[doc],
                                      **self._dataset_for_table(table, dataset))
            yield doc, doc_pessoa['id_doc_pessoa']

    def retifica_dados(self, dataset):
        cpf = dataset['cpf']
        if not validate_cpf(cpf):
            raise InvalidDatasetException(dataset, msg="CPF inválido")

        dataset['cpf'] = format_cpf(cpf)

        if not dataset.get('nome_social'):
            dataset['nome_social'] = dataset['nome_pessoa']

    @as_transaction
    def perform_work(self, dataset, commit):
        dataset.update(self.constants)

        self.retifica_dados(dataset)

        pessoa = self.criar_pessoa(dataset)
        dataset.update(pessoa)

        dataset['id_doc_pessoa'] = dict(self.criar_documentos(dataset))

        return dataset







