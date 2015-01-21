dbSie.define_table(
    "V_SERVIDORES_EMAIL",
    Field("ID_PESSOA", "integer"),
    Field("NOME_PESSOA", "string"),
    Field("DESCR_MAIL", "string"),
    primarykey=["ID_PESSOA"],
    migrate=False,
    rname="DBSM.V_SERVIDORES_EMAIL"
)