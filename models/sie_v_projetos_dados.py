dbSie.define_table(
    "V_PROJETOS_DADOS",
    Field("ID_PROJETO" , "integer"),
    Field("TITULO", "string"),
    Field("SITUACAO", "string"),
    Field("NOME_DISCIPLINA", "string"),
    Field("DT_REGISTRO", "date"),
    Field("DESCRICAO", "string"),
    Field("COORDENADOR", "string"),
    Field("AVALIACAO", "string"),
    primarykey=["ID_PROJETO"],
    migrate=False,
    rname="DBSM.V_PROJETOS_DADOS"
)