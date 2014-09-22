# -*- coding: utf-8 -*-
dbSie.define_table( "COLUMNS",
                    Field("TABSCHEMA", "string"),
                    Field("TABNAME", "string"),
                    Field("COLNAME", "string"),
                    Field("COLNO", "string"),
                    Field("TYPENAME", "string"),
                    Field("LENGTH", "string"),
                    Field("SCALE", "string"),
                    Field("REMARKS", "string"),
                    primarykey=["TABSCHEMA", "COLNAME", "TABNAME"],
                    migrate=False,
                    rname='SYSCAT.COLUMNS'
                    )