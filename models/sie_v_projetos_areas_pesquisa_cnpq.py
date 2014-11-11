dbSie.define_table("V_PROJETOS_AREAS_PESQUISA_CNPQ",
                   Field("ID_AREA", "string"),
                   Field("AREA_CNPQ", "string"),
                   primarykey=["ID_AREA"],
                   migrate=False,
                   rname='DBSM.V_PROJETOS_AREAS_PESQUISA_CNPQ'
)