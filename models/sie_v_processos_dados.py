# -*- coding: utf-8 -*-
dbSie.define_table("V_PROCESSOS_DADOS",
                   Field("ID_DOCUMENTO", "integer"),
                   Field("NUM_PROCESSO", "string"),
                   Field("RESUMO_ASSUNTO", "string"),
                   Field("EMITENTE", "string"),
                   Field("DT_ALTERACAO", "date"),
                   Field("HR_ALTERACAO", "time"),
                   Field("DESCR_ASSUNTO", "string"),
                   Field("COD_ESTRUTURADO", "string"),
                   Field("NOME_INTERESSADO", "string"),
                   Field("PROCEDENCIA", "string"),
                   Field("NOME_TIPO_INTERESSADO", "string"),
                   primarykey=['NUM_PROCESSO'],
                   migrate=False,
                   rname='DBSM.V_PROCESSOS_DADOS'
                   )