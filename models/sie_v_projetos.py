dbSie.define_table("V_PROJETOS",
    Field("UNIDADE_RESPONSAVEL", "string"),
    Field("TITULO", "string"),
    Field("RESUMO", "text"),
    Field("ID_PROJETO", "integer"),
    Field("GRUPO_CNPQ", "string"),
    Field("DT_INICIAL", "date"),
    Field("DESCR_MAIL", "string"),
    Field("COORDENADOR", "string"),
    Field("CLASSIFICAO_CNPQ", "string"),
    Field("ANO_REFERENCIA", "integer")
)