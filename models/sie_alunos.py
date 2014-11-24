# -*- coding: utf-8 -*-
dbSie.define_table( "ALUNOS",
                    Field("ID_ALUNO", "integer"),
                    Field("ID_PESSOA", "integer"),
                    Field("ID_NATURALIDADE", "integer"),
                    Field("SEXO", "integer"),
                    Field("DT_NASCIMENTO", "date"),
                    Field("ETNIA_ITEM", "integer"),
                    Field("ETNIA_TAB", "integer"),
                    primarykey=["ID_ALUNO"],
                    migrate=False
                    )
