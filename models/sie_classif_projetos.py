# -*- coding: utf-8 -*-

dbSie.define_table("CLASSIF_PROJETOS",
                   Field("ID_CLASSIF_PROJETO","integer"),
                   Field("ID_PROJETO","integer"),
                   Field("ID_CLASSIFICACAO","integer"),
                   Field("COD_OPERADOR","integer"),
                   Field("DT_ALTERACAO","date"),
                   Field("HR_ALTERACAO","time"),
                   Field("CONCORRENCIA","integer"),
                   Field("ENDERECO_FISICO"),
                   primarykey=["ID_CLASSIF_PROJETO"],
                   migrate=False)