dbSie.define_table("V_PROJETOS_AREAS_CONHECIMENTO",
    Field("ID_CLASSIFICACAO", "integer"),
    Field("DESCRICAO", "string"),
    Field("CLASSIFICACAO_ITEM", "string"),
    primarykey=["ID_CLASSIFICACAO"],
    migrate=False,
    rname='DBSM.V_PROJETOS_AREAS_CONHECIMENTO'
)