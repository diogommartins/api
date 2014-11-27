# -*- coding: utf-8 -*-

dbSie.define_table("NUMEROS_TIPO_DOC",
                   Field("ID_NUMERO_TIPO_DOC", "integer"),
                   Field("ID_TIPO_DOC", "integer"),
                   Field("ANO_TIPO_DOC", "integer"),
                   Field("NUM_ULTIMO_DOC", "integer"),
                   Field("IND_DEFAULT", "string"),
                   Field("COD_OPERADOR", "integer"),
                   Field("DT_ALTERACAO", "date"),
                   Field("HR_ALTERACAO", "time"),
                   Field("CONCORRENCIA", "integer"),
                   Field("ENDERECO_FISICO", "string"),
                   primarykey=["ID_NUMERO_TIPO_DOC"],
                   migrate=False)
