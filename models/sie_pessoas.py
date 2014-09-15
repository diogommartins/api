#-*- coding: utf-8 -*-
dbSie.define_table( "PESSOAS",
                    Field("ID_PESSOA", "integer"),
                    Field("NOME_PESSOA", "string"),
                    Field("NOME_PESSOA_UP", "string"),
                    Field("NATUREZA_JURIDICA", "string"),
                    Field("NOME_SOCIAL", "string"),
                    primarykey=["ID_PESSOA"],
                    migrate=False
                    )
