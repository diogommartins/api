# -*- coding: utf-8 -*-

# Requer sie_tab_estruturada
# Requer sie_versoes_cursos

dbSie.define_table( "CURSOS_ALUNOS",
                    Field("ID_CURSO_ALUNO", "integer"),
                    Field("ID_VERSAO_CURSO", "integer"),
                    Field("ID_ALUNO", "integer"),
                    Field("FORMA_INGRE_ITEM", "integer"),
                    Field("FORMA_INGRE_TAB", "integer"),
                    Field("FORMA_EVASAO_ITEM", "integer"),
                    Field("FORMA_EVASAO_TAB", "integer"),
                    Field("UF_ALUNO_ITEM", "integer"),
                    Field("UF_ALUNO_TAB", "integer"),
                    Field("ANO_INGRESSO", "integer"),
                    Field("ANO_EVASAO", "integer"),
                    Field("PERIODO_ATUAL", "integer"),
                    Field("DT_INGRESSO", "date"),
                    Field("DT_CONCLUSAO", "date"),
                    primarykey=["ID_CURSO_ALUNO"],
                    migrate=False
                    )
