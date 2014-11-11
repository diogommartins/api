dbSie.define_table("V_PROJETOS_GRUPO_CNPQ",
                   Field("ID_CLASSIFICACAO", "integer"),
                   Field("GRUPO_CNPQ", "string"),
                   migrate=False,
                   rname='DBSM.V_PROJETOS_GRUPO_CNPQ'
)