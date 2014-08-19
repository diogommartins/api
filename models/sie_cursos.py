# -*- coding: utf-8 -*-
#CLASSIF_CURSO_ITEM: 1 - Presencial    2 - EAD
dbSie.define_table( "CURSOS",
                    Field("ID_CURSO", "integer"),
                    Field("ID_UNIDADE", "integer"),
                    Field("ID_VERSAO_CORRENTE", "integer"),
                    Field("ID_CURSO", "integer"),
                    Field("ID_CURSO", "integer"),
                    Field("DOC_RECONHECIMENTO", "string"),
                    Field("DOC_AUTORIZACAO", "string"),
                    Field("DESCR_GRAU", "string"),
                    Field("COD_CURSO", "string"),
                    Field("NOME_CURSO_DIPLOMA", "string"),
                    Field("CONCEITO_MEC_ITEM", "integer"),
                    Field("CLASSIF_CURSO_ITEM", "integer"),
                    primarykey=["ID_CURSO"],
                    migrate=False
                    )

#dbSie.CURSOS.CONCEITO_MEC_ITEM.requires = [IS_IN_DB(dbSie, '')]