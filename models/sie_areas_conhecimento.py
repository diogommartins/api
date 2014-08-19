# -*- coding: utf-8 -*-
dbSie.define_table( "AREAS_CONHECIMENTO",
                    Field("ID_AREA_CONHEC", "integer"),
                    Field("ID_AREA_CONHEC_SUP", "integer"),
                    Field("COD_AREA_CONHEC", "string"),
                    Field("COD_ESTRUTURADO", "string"),
                    Field("DESCR_AREA_CONHEC", "string"),
                    primarykey=["ID_AREA_CONHEC"],
                    migrate=False
                    )