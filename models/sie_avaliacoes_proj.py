__author__ = 'sigin'
# -*- coding: utf-8 -*-

dbSie.define_table("AVALIACOES_PROJ",
                   Field("ID_AVALIACAO_PROJ", "integer"),
                   Field("ID_PROJETO", "integer"),
                   Field("ID_DOCUMENTO", "integer"),
                   Field("ID_CONTRATO_RH", "integer"),
                   Field("ID_UNIDADE", "integer"),
                   Field("ANO_REF", "integer"),
                   Field("PERIODO_REF_TAB", "integer"),
                   Field("PERIODO_REF_ITEM", "integer"),
                   Field("TIPO_AVAL_TAB", "integer"),
                   Field("TIPO_AVAL_ITEM", "integer"),
                   Field("SITUACAO_TAB", "integer"),
                   Field("SITUACAO_ITEM", "integer"),
                   Field("NUM_PROCESSO", "string"),
                   Field("DT_CONCLUSAO", "date"),
                   Field("OBS_PRORROGACAO", "string"),
                   #Field("RESULTADOS_OBTIDOS", "clob"),
                   Field("COD_OPERADOR", "integer"),
                   Field("DT_ALTERACAO", "date"),
                   Field("HR_ALTERACAO", "time"),
                   Field("CONCORRENCIA", "integer"),
                   Field("ENDERECO_FISICO", "string"),
                   primarykey=["ID_AVALIACAO_PROJ"],
                   migrate=False)


