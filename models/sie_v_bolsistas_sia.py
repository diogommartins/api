# -*- coding: utf-8 -*-
dbSie.define_table("V_BOLSISTAS_SIA",
                   Field("ID_CURSO_ALUNO", "integer"),
                   Field("ID_PESSOA", "integer"),
                   Field("NOME_PESSOA", "string"),
                   Field("CPF_MASCARA", "string"),
                   Field("CPF", "string"),
                   Field("MATR_ALUNO", "string"),
                   Field("NOME_CURSO_DIPLOMA", "string"),
                   Field("ANO", "integer"),
                   Field("COD_BOLSA", "string"),
                   Field("ID_BOLSA", "integer"),
                   primarykey=['ID_CURSO_ALUNO'],
                   migrate=False,
                   rname='DBSM.V_BOLSISTAS_SIA'
                   )