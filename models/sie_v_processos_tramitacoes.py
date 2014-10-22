# -*- coding: utf-8 -*-
dbSie.define_table("V_PROCESSOS_TRAMITACOES",
                   Field("NUM_PROCESSO", "string"),
                   Field("DT_ENVIO", "string"),
                   Field("DESCR_FLUXO", "string"),
                   Field("DT_RECEBIMENTO", "string"),
                   Field("ID_ORIGEM", "integer"),
                   Field("TIPO_ORIGEM", "integer"),
                   Field("ID_DESTINO", "string"),
                   Field("TIPO_DESTINO", "string"),
                   Field("DESPACHO", "string"),
                   Field("SITUACAO_TRAMIT", "string"),
                   Field("RECEBIDO", "string"),
                   Field("ORIGEM", "string"),
                   Field("DESTINO", "string"),
                   primarykey=['NUM_PROCESSO', 'DT_ENVIO', 'DT_RECEBIMENTO'],
                   migrate=False,
                   rname='DBSM.V_PROCESSOS_TRAMITACOES'
                   )
