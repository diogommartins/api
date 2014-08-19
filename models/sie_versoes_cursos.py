# -*- coding: utf-8 -*-
dbSie.define_table( "VERSOES_CURSOS",
                    Field("ID_VERSAO_CURSO", "integer"),
                    Field("ID_VERSAO_CUR_ANT", "integer"), #FK pra VERSOES_CURSOS
                    Field("ID_CURSO", "integer"),
                    Field("COD_INTEGRACAO", "string", label="Cod. EMEC/Capes"),
                    Field("CH_TOTAL", "integer", label="Carga horária total"),
                    Field("DESCR_VERSAO", "string"),
                    Field("NOME_CURSO_DIPLOMA", "string"),
                    Field("OBSERVACOES", "string"),
                    Field("SITUACAO_VERSAO", "string", length=1),
                    primarykey=["ID_VERSAO_CURSO"],
                    migrate=False
                    )