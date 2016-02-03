# coding=utf-8
from datetime import date, datetime, timedelta
from time import strftime

from .base import BaseSIEProcedure
from .exceptions import ProcedureDatasetException
import abc

__all__ = ('CriarDocumentoProjetoPesquisa',)


class CriarDocumento(BaseSIEProcedure):
    __metaclass__ = abc.ABCMeta

    # Valores de prioridade de documento

    TRAMITACAO_PRIORIDADE_NORMAL = 2

    # Valores validos para SITUACAO_TRAMIT

    TRAMITACAO_SITUACAO_AGUARDANDO = "T"
    TRAMITACAO_SITUACAO_ENTREGUE = "E"
    TRAMITACAO_SITUACAO_RECEBIDO = "R"

    # Valores validos para IND_RETORNO_OBRIG

    TRAMITACAO_IND_RETORNO_OBRIG_SIM = "S"
    TRAMITACAO_IND_RETORNO_OBRIG_NAO = "N"
    TRAMITACAO_IND_RETORNO_OBRIG_CONFORME_FLUXO = "F"

    @abc.abstractproperty
    def TIPO_DOCUMENTO(self):
        raise NotImplementedError("Todas as subclasses são um tipo de documento, "
                                  "portanto, devem ter um atributo TIPO_DOCUMENTO")

    @property
    def required_fields(self):
        super_required = super(CriarDocumento, self).required_fields
        required = {
            'ID_CRIADOR': 'int',  # ID_USUARIO
            'ID_INTERESSADO': 'int',  # ID_CONTRATO_RH
            'ID_PROCEDENCIA': 'int',  # ID_CONTRATO_RH
            'ID_PROPRIETARIO': 'int',  # ID_USUARIO
            'ID_USUARIO': 'int'  # ID_USUARIO
        }
        required.update(super_required)
        return required

    @property
    def constants(self):
        super_consts = super(CriarDocumento, self).constants
        consts = {
            "DT_CRIACAO": date.today(),
            "HR_CRIACAO": datetime.now().time().strftime("%H:%M:%S"),
            "IND_DEFAULT": "S",
            "SITUACAO_ATUAL": 1,  # Um novo documento sempre se inicia com 1
            "TEMPO_ESTIMADO": 1,
        }
        consts.update(super_consts)
        return consts

    def _assunto_relacionado(self, ID_ASSUNTO):
        return self.datasource(self.datasource.ASSUNTOS.ID_ASSUNTO == ID_ASSUNTO).select().first()

    def _get_dt_limit_arquivamento(self, TEMPO_ARQUIVAMENTO):
        """
        :type TEMPO_ARQUIVAMENTO: int
        :rtype: date
        """
        return date.today() + timedelta(days=int(TEMPO_ARQUIVAMENTO))

    # mark - Documentos

    def _criar_novo_numero_tipo_doc(self, ano):
        """
        :return: NUM_ULTIMO_DOC da inserção
        :rtype: int
        """
        num_ultimo_doc = 1
        self.datasource.NUMEROS_TIPO_DOC.insert(ID_TIPO_DOC=self.TIPO_DOCUMENTO,
                                                ANO_TIPO_DOC=ano,
                                                IND_DEFAULT="S",
                                                NUM_ULTIMO_DOC=num_ultimo_doc)
        return num_ultimo_doc

    def _proximo_num_tipo_doc(self, ano):
        """
        :type ano: int
        :type ID_TIPO_DOC: int
        :rtype: int
        """
        table = self.datasource.NUMEROS_TIPO_DOC
        row = self.datasource((table.ID_TIPO_DOC == self.TIPO_DOCUMENTO) &
                              (table.ANO_TIPO_DOC == ano)).select(table.NUM_ULTIMO_DOC).first()
        if row:
            ultimo_numero = row['NUM_ULTIMO_DOC'] + 1
            self._atualizar_num_tipo_doc_contador(ultimo_numero, ano)
            return ultimo_numero
        else:
            # Não existe uma entrada na tabela para este tipo de documento e portanto, devemos criar
            ultimo_numero = self._criar_novo_numero_tipo_doc(ano)
            return ultimo_numero

    def _atualizar_num_tipo_doc_contador(self, valor, ano):
        table = self.datasource.NUMEROS_TIPO_DOC
        self.datasource((table.ID_TIPO_DOC == self.TIPO_DOCUMENTO) &
                        (table.ANO_TIPO_DOC == ano)).update(NUM_ULTIMO_DOC=valor,
                                                            DT_ALTERACAO=date.today(),
                                                            HR_ALTERACAO=datetime.now().time().strftime("%H:%M:%S"))

    @abc.abstractmethod
    def _numero_processo_parser(self, numero, ano):
        raise NotImplementedError

    def _tipo_doc(self):
        table = self.datasource.TIPOS_DOCUMENTOS
        return self.datasource(table.ID_TIPO_DOC == self.TIPO_DOCUMENTO).select(cache=self.cache).first()

    def _assunto(self, ID_ASSUNTO):
        table = self.datasource.ASSUNTOS
        return self.datasource(table.ID_ASSUNTO == ID_ASSUNTO).select(cache=self.cache).first()

    def _gerar_numero_processo(self, ID_TIPO_DOC):
        """
        Gera o proximo numero de processo a ser usado, formado de acordo com a mascara do tipo de documento.

        :rtype: str
        :return: Retorna o NUM_PROCESSO gerado a partir da logica de negocio
        """
        # mascara = self._obter_mascara(ID_TIPO_DOC) # Desnecessário
        ano = date.today().year
        proximo_numero = self._proximo_num_tipo_doc(ano)
        return self._numero_processo_parser(proximo_numero, ano)

    # mark - tramitacoes

    def _obter_fluxo_inicial(self):
        table = self.datasource.FLUXOS
        return self.datasource((table.ID_TIPO_DOC == self.TIPO_DOCUMENTO) &
                               (table.SITUACAO_ATUAL == 1) &
                               (table.IND_ATIVO == 'S')).select().first()

    def _tramitacao_atual(self, ID_DOCUMENTO):
        table = self.datasource.TRAMITACOES
        return self.datasource((table.ID_DOCUMENTO == ID_DOCUMENTO)).select(orderby=~table.SEQUENCIA).first()

    def _tramitar_documento(self, fluxo, dataset):
        tramitacao_atual = self._tramitacao_atual(dataset['ID_DOCUMENTO'])

        definido_externamente = lambda f: f['IND_QUERY'].strip() == 'S'

        if definido_externamente(tramitacao_atual):
            raise NotImplementedError("Não suporta fluxos do tipo IND_QUERY")

        dt_validade = lambda data, dias: data + timedelta(days=dias)

        tramitacao_atual.update({
            "TIPO_DESTINO": fluxo["TIPO_DESTINO"],
            "ID_DESTINO": fluxo["ID_DESTINO"],
            "DT_ENVIO": date.today(),
            "DT_VALIDADE": dt_validade(date.today(), fluxo["NUM_DIAS"]),
            "DESPACHO": fluxo["TEXTO_DESPACHO"],
            "DESPACHO_RTF": fluxo["TEXTO_DESPACHO"],
            "SITUACAO_TRAMIT": self.TRAMITACAO_SITUACAO_ENTREGUE,
            "IND_RETORNO_OBRIG": self.TRAMITACAO_IND_RETORNO_OBRIG_CONFORME_FLUXO,
            "ID_FLUXO": fluxo["ID_FLUXO"],
            "DT_ALTERACAO": date.today(),
            "HR_ALTERACAO": strftime("%H:%M:%S"),
            "CONCORRENCIA": tramitacao_atual["CONCORRENCIA"] + 1,
            "ID_USUARIO_INFO": dataset["ID_USUARIO"],
            "DT_DESPACHO": date.today(),
            "HR_DESPACHO": strftime("%H:%M:%S"),
            "ID_APLIC_ACAO": fluxo["ID_APLIC_ACAO"]
        })

        table = self.datasource.TRAMITACOES
        result = self.datasource(table.ID_TRAMITACAO == tramitacao_atual['ID_TRAMITACAO']).update(tramitacao_atual)
        pass


class CriarDocumentoProjetoPesquisa(CriarDocumento):
    TIPO_DOCUMENTO = 217

    @property
    def required_fields(self):
        super_required = super(CriarDocumentoProjetoPesquisa, self).required_fields
        required = {
            'TEMPO_ARQUIVAMENTO': 'int'
        }
        required.update(super_required)
        return required

    @property
    def constants(self):
        super_consts = super(CriarDocumentoProjetoPesquisa, self).constants
        consts = {
            "IND_AGENDAMENTO": "N",  # doc sintese
            "IND_ELIMINADO": "N",  # doc sintese
            "IND_EXTRAVIADO": "N",  # doc sintese
            "IND_RESERVADO": "N",  # doc sintese
            "TEMPO_ESTIMADO": 1,  # doc sintese
            "TIPO_INTERESSADO": "S",  # Indica servidor
            "TIPO_PROCEDENCIA": "S",  # Indica servidor
            "TIPO_PROPRIETARIO": 20,  # Indica a restrição de usuário
        }
        consts.update(self._tipo_doc())
        consts.update(self._assunto(consts['ID_ASSUNTO_PADRAO']))
        consts['RESUMO_ASSUNTO'] = consts['DESCR_ASSUNTO']
        consts.update(super_consts)
        return consts

    def _obter_parametros_tipo_documento(self):
        return self.datasource(self.datasource.TIPOS_DOCUMENTOS.ID_TIPO_DOC == self.TIPO_DOCUMENTO).select().first()

    def _numero_processo_parser(self, numero, ano):
        return "{tipo}{numero}/{ano}".format(tipo='P',
                                             numero=str(numero).zfill(4),
                                             ano=ano)

    def perform_work(self, dataset):
        """

        * [1] Gera número de processo para novo documento
        * [2] Insere uma nova entrada na tabela DOCUMENTOS
        * [3] Insere uma nova entrada na tabela TRAMITACOES
        * [4] Insere uma nova entrada na tabela ESTADOS_DOCUMENTOS

        :type dataset: dict
        """
        # todo Não deveria ser necessário reconectar, mas após o final de uma requisição, o web2py fecha todas as conexoes
        if not self.datasource._adapter.connection:
            self.datasource._adapter.reconnect()

        dataset.update(self.constants)
        try:
            # 1
            if 'NUM_PROCESSO' not in dataset:
                dataset['NUM_PROCESSO'] = self._gerar_numero_processo(self.TIPO_DOCUMENTO)

            # 2
            documento = self._dataset_for_table(self.datasource.DOCUMENTOS, dataset)
            self.datasource.DOCUMENTOS.insert(**documento)

            # 3
            # fluxo_inicial = self._obter_fluxo_inicial()
            # self._tramitar_documento(fluxo_inicial, dataset)
            self.datasource.TRAMITACOES.insert(
                    SEQUENCIA=1,  # Primeiro passo da tramitacao
                    DT_ENVIO=date.today(),
                    SITUACAO_TRAMIT=self.TRAMITACAO_SITUACAO_AGUARDANDO,
                    IND_RETORNO_OBRIG=self.TRAMITACAO_IND_RETORNO_OBRIG_NAO,
                    PRIORIDADE_TAB=5101,  # nivel de prioridade
                    PRIORIDADE_ITEM=self.TRAMITACAO_PRIORIDADE_NORMAL,
                    **self._dataset_for_table(self.datasource.TRAMITACOES, dataset)
            )

            tramitacao = self.datasource(self.datasource.TRAMITACOES.ID_TRAMITACAO == dataset['ID_TRAMITACAO']).select().first()
            dataset.update(tramitacao)

            # 4
            COD_TABELA_SITUACAO_DOCUMENTO = 2001
            ITEM_SITUACAO_DOCUMENTO_ATIVO = 1

            self.datasource.ESTADOS_DOCUMENTOS.insert(
                    COD_SITUACAO_TAB=COD_TABELA_SITUACAO_DOCUMENTO,
                    COD_SITUACAO_ITEM=ITEM_SITUACAO_DOCUMENTO_ATIVO,
                    **self._dataset_for_table(self.datasource.ESTADOS_DOCUMENTOS, dataset)
            )

            # self.datasource.commit()
            self.datasource.rollback()
            return dataset
        except Exception as e:
            self.datasource.rollback()
            raise ProcedureDatasetException(dataset, e)
