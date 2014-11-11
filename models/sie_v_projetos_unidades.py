dbSie.define_table("V_PROJETOS_UNIDADES",
                   Field("ID_UNIDADE", "integer"),
                   Field("NOME_UNIDADE", "string"),
                   primarykey=["ID_UNIDADE"],
                   migrate=False,
                   rname='DBSM.V_PROJETOS_UNIDADES'
)