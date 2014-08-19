# -*- coding: utf-8 -*-
dbSie.define_table( "CIDADES",
                    Field("ID_CIDADE", "integer"),
                    Field("NOME_CIDADE", "string"),
                    Field("UF_CIDADE_TAB", "integer"),
                    Field("UF_CIDADE_ITEM", "integer"),
                    Field("COD_IBGE", "string"),
                    Field("CRE_TAB", "integer"),
                    Field("CRE_ITEM", "integer"),
                    Field("MICRO_REGIAO_TAB", "integer"),
                    Field("MICRO_REGIAO_ITEM", "integer"),
                    Field("GRUPO_CIDADE_TAB", "integer"),
                    Field("GRUPO_CIDADE_ITEM", "integer"),
                    primarykey=["ID_CIDADE"],
                    migrate=False
                    )