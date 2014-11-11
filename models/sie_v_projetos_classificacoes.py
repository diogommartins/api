dbSie.define_table("V_PROJETOS_CLASSIFICACOES",
                   Field("CLASSIFICACAO", "string"),
                   Field("TIPO_CLASSIFICACAO", "string"),
                   primarykey=["CLASSIFICACAO"],
                   migrate=False,
                   rname='DBSM.V_PROJETOS_CLASSIFICACOES'
)