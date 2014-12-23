# -*- coding: utf-8 -*-

dbSie.define_table("ARQUIVOS_PROJ",
                   Field("ID_ARQUIVO_PROJ", "integer"),
                   Field("ID_PROJETO", "integer"),
                   Field("DT_INCLUSAO", "date"),
                   Field("TIPO_ARQUIVO_TAB", "integer"),
                   Field("TIPO_ARQUIVO_ITEM", "integer"),
                   Field("NOME_ARQUIVO", "string"),
                   Field("CONTEUDO_ARQUIVO", "blob"),
                   Field("OBSERVACAO", "string"),
                   Field("COD_OPERADOR", "integer"),
                   Field("DT_ALTERACAO", "date"),
                   Field("HR_ALTERACAO", "time"),
                   Field("CONCORRENCIA", "integer"),
                   Field("ID_AVALIACAO_PROJ", "integer"),
                   Field("ID_ARQUIVO_SUP", "integer"),
                   Field("ENDERECO_FISICO", "string"),
                   primarykey=["ID_ARQUIVO_PROJ"],
                   migrate=False)

