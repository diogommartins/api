dbSie.define_table(
    "V_PROJETOS_DADOS",
    Field("ID_PROJETO" , "integer"),
    Field("NUM_PROCESSO", "string"),
    Field("TITULO", "string"),
    Field("SITUACAO", "string"),
    Field("NOME_DISCIPLINA", "string"),
    Field("DT_REGISTRO", "date"),
    Field("DESCRICAO", "string"),
    Field("ID_PESSOA", "integer"),
    Field("COORDENADOR", "string"),
    Field("AVALIACAO", "string"),
    Field("ID_CLASSIFICAO", "integer"),
    Field("NOME_CURSO", "string"),
    primarykey=["ID_PROJETO"],
    migrate=False,
    rname="DBSM.V_PROJETOS_DADOS"
)