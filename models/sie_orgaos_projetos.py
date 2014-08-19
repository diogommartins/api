# -*- coding: utf-8 -*-
dbSie.define_table("ORGAOS_PROJETOS",
                   Field("ID_ORGAO_PROJETO", "integer"),
                   Field("ID_PROJETO", "integer"),
                   Field("ID_UNIDADE", "integer"),
                   Field("ID_ENT_EXTERNA", "integer"),
                   Field("FUNCAO_ORG_TAB", "integer"),
                   Field("FUNCAO_ORG_ITEM", "integer"),
                   Field("DT_INICIAL", "date"),
                   Field("DT_FINAL", "date"),
                   Field("VL_CONTRIBUICAO", "float"),
                   Field("OBS_ORG_PROJETO", "string"),
                   Field("DT_ALTERACAO", "date"),
                   Field("HR_ALTERACAO", "time"),
                   Field("CONCORRENCIA", "integer"),
                   Field("SITUACAO", "string", length=1),
                   primarykey=['ID_ORGAO_PROJETO'],
                   migrate=False
                   )