# -*- coding: utf-8 -*-
dbSie.define_table( "TAB_ESTRUTURADA",
                    Field("ID_TABELA", "integer"),
                    Field("ITEM_TABELA", "integer"),
                    Field("COD_TABELA", "integer"),
                    Field("DESCRICAO", "string"),
                    primarykey=["ID_TABELA"],
                    migrate=False
                    )
