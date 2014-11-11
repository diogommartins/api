dbSie.define_table("V_PROJETOS_CLASSIFICACOES",
                   Field("CLASSIFICACAO", "string"),
                   Field("TIPO_CLASSIFICACAO", "string"),
                   migrate=False,
                   rname='DBSM.V_PROJETOS_CLASSIFICACOES'
)