dbSie.define_table( "V_FORMA_INGRESSO",
                    Field("ITEM_TABELA", "integer"),
                    Field("POSICAO_CENSO", "integer"),
                    Field("DESCRICAO", "string", length=100),
                    Field("DESCR_CENSO", "string", length=25),
                    primarykey=["ITEM_TABELA"],
                    migrate=False
                     )