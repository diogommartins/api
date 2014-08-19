# -*- coding: utf-8 -*-
dbSie.define_table( "DISCIPLINAS",
                    Field("ID_DISCIPLINA", "integer"),
                    Field("COD_DISCIPLINA", "string"),
                    Field("NOME_DISCIPLINA", "string"),
                    Field("TIPO_ATIV_TAB", "integer"), # tab estrurada
                    Field("TIPO_ATIV_ITEM", "integer"), # tab estrurada
                    Field("NOME_DISCIPLINA", "string"),
                    Field("CH_TEORICA", "integer", label="Carga horária teórica"),
                    Field("CH_PRATICA", "integer", label="Carga horária prática"),
                    Field("CH_TOTAL", "integer", label="Carga horária total"),
                    Field("CREDITOS", "integer", label="Cod. EMEC/Capes"),
                    Field("ID_AREA_CONHEC", "integer"),
                    Field("ID_UNIDADE", "integer"),
                    Field("CONCORRENCIA", "integer"),
                    Field("SITUACAO", "string", length=1),
                    primarykey=["ID_DISCIPLINA"],
                    migrate=False
                    )