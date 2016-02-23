import abc
from procedures.documento import CriarDocumentoProjetoPesquisa


class CadastrarProjeto(CriarDocumentoProjetoPesquisa):
    __metaclass__ = abc.ABCMeta

    @property
    def required_fields(self):
        super_required = super(CriarDocumentoProjetoPesquisa, self).required_fields
        required = {
            'TITULO': 'string',
            'DT_INICIAL': 'date',
            'DT_REGISTRO': 'date',
            'TIPO_PUBLICO_TAB': 'int',
            'TIPO_PUBLICO_ITEM': 'int',
            'ACESSO_PARTICIP': 'string',
            'EVENTO_TAB': 'int',
            'EVENTO_ITEM': 'int',
            'PAGA_BOLSA': 'string'
        }
        required.update(super_required)
        return required