# coding=utf-8
from procedures.base import BaseSIEProcedure
from procedures.exceptions import ProcedureDatasetException


class TramitacoesComoGrafo(BaseSIEProcedure):
    @property
    def required_fields(self):
        super_required = super(TramitacoesComoGrafo, self).required_fields
        required = {
            'ID_DOCUMENTO': 'int'
        }
        required.update(super_required)
        return required

    @property
    def view(self):
        return self.datasource.V_TRAMITACOES_DETALHES

    @property
    def situacoes_finalizadas(self):
        return 777, 999

    def trim_strings(self, documento):
        for k, v in documento.iteritems():
            if isinstance(v, str):
                documento[k] = v.rstrip()
        return documento

    def convert_names_cases(self, documento):
        for name in ('ORIGEM', 'DESTINO', 'RECEBIDO'):
            documento[name] = documento[name].title()
        return documento

    def to_element(self, item, estatistica):
        elem = {
            'data': {
                'elementId': 'edge_' + str(item['ID_FLUXO']),
                'estatistica': estatistica,
            },
            'group': 'edges'
        }
        self.trim_strings(item)
        self.convert_names_cases(item)

        elem['data'].update(item)

        return elem

    def get_estatisticas(self, id_tipo_doc):
        table = self.datasource.V_TRAMITACOES_ESTATISTICAS
        result = self.datasource(table.ID_TIPO_DOC == id_tipo_doc).select(
            table.ID_FLUXO,
            table.MEDIA_DIFERENCA,
            table.QUANTIDADE
        )
        return {item.ID_FLUXO: {'media': item.MEDIA_DIFERENCA, 'quantidade': item.QUANTIDADE} for item in result}

    def perform_work(self, dataset, commit=False):
        result = self.datasource(self.view.ID_DOCUMENTO == dataset['ID_DOCUMENTO']).select(orderby=self.view.SEQUENCIA)

        documento = self.datasource(self.datasource.DOCUMENTOS.ID_DOCUMENTO == dataset['ID_DOCUMENTO']).select(
            self.datasource.DOCUMENTOS.ID_TIPO_DOC,
            self.datasource.DOCUMENTOS.NUM_PROCESSO,
            self.datasource.DOCUMENTOS.SITUACAO_ATUAL,
            self.datasource.DOCUMENTOS.EMITENTE,
            self.datasource.DOCUMENTOS.RESUMO_ASSUNTO,
        ).first()

        if not documento:
            raise ProcedureDatasetException(dataset, msg='ID_DOCUMENTO inválido')

        estatisticas = self.get_estatisticas(documento.ID_TIPO_DOC)
        tramitacoes = [self.to_element(tramitacao, estatisticas[tramitacao.ID_FLUXO]) for tramitacao in result]

        result_dataset = {
            'items': tramitacoes,
            'id_tipo_doc': documento.ID_TIPO_DOC,
            'num_processo': documento.NUM_PROCESSO,
            'isFinalizado': documento.SITUACAO_ATUAL in self.situacoes_finalizadas,
            'emitente': documento.EMITENTE.rstrip(),
            'assunto': documento.RESUMO_ASSUNTO.rstrip()
        }
        return result_dataset
