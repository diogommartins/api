dbSie.define_table("V_PROJETOS_CLASSIFICACOES",
                   Field("ID_PROJETO"),
                   Field("CLASSIFICACAO", "string"),
                   Field("TIPO_CLASSIFICACAO", "string"),
                   primarykey=["ID_PROJETO", "CLASSIFICACAO", "TIPO_CLASSIFICACAO"],
                   migrate=False,
                   rname='DBSM.V_PROJETOS_CLASSIFICACOES'
)