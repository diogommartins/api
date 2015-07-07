from applications.api.modules.procedures.base import BaseProcedure


class MatricularAlunos(BaseProcedure):
    required_fields = frozenset(
        [
            "COD_CURSO",
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
