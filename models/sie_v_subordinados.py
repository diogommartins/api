# -*- coding: utf-8 -*-
dbSie.define_table("V_SUBORDINADOS",
                   Field("SIAPE_CHEFIA", "integer"),
                   Field("SIAPE_SUBORDINADO", "integer"),
                   Field("NOME_SUBORDINADO", "string"),
                   Field("CPF_CHEFIA_MASCARA", "string"),
                   Field("CPF_CHEFIA", "string"),
                   Field("CPF_SUBORDINADO_MASCARA", "string"),
                   primarykey=["SIAPE_CHEFIA", "SIAPE_SUBORDINADO"],
                   migrate=False,
                   rname="DBSM.V_SUBORDINADOS"
                   )