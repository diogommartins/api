#-*- coding: utf-8 -*-
dbSie.define_table( "PESSOAS",
                    Field("ID_PESSOA", "integer"),
                    Field("NOME_PESSOA", "string"),
                    Field("NOME_PESSOA_UP", "string"),
                    Field("NATUREZA_JURIDICA", "string"),
                    Field("COD_OPERADOR", "string"),
                    Field("DT_ALTERACAO", "date"),
                    Field("HR_ALTERACAO", "time"),
                    Field("CONCORRENCIA", "integer"),
                    Field("NOME_SOCIAL", "string"),
                    Field("ENDERECO_FISICO", "string"),
                    primarykey=["ID_PESSOA"],
                    migrate=False
                    )
