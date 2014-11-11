dbSie.define_table("V_PROJETOS_PARTICIPANTES",
                   Field("NOME_PESSOA", "string"),
                   Field("ID_PROJETO", "integer"),
                   Field("FUNCAO", "string"),
                   Field("DESCR_MAIL", "string"),
                   Field("VINCULO", "string"),
                   Field("DT_INICIAL", "date"),
                   Field("DT_FINAL", "date"),
                   Field("FUNCAO_ITEM", "integer"),
                   primarykey=["ID_PROJETO", "FUNCAO_ITEM", "NOME_PESSOA"],
                   migrate=False,
                   rname='DBSM.V_PROJETOS_PARTICIPANTES'
)