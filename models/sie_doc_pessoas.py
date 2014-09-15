#2-*- coding: utf-8 -*-
dbSie.define_table( "DOC_PESSOAS",
                    Field("ID_DOC_PESSOA", "integer"),
                    Field("ID_TDOC_PESSOA", "integer"),
                    Field("ID_PESSOA", "integer"),
                    Field("NUMERO_DOCUMENTO", "string"),
                    Field("ORGAO_EMISSOR", "string"),
                    Field("DT_EXPEDICAO", "date"),
                    Field("DT_VALIDADE", "date"),
                    Field("UF_TAB", "integer"),
                    Field("UF_ITEM", "integer"),
                    primarykey=["ID_DOC_PESSOA"],
                    migrate=False
                    )
