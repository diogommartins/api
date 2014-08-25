# -*- coding: utf-8 -*-
dbSie.define_table("DIARIO_CLASSE",
                   Field("CURSO_DO_ALUNO", "string", length=10),
                   Field("ID_ALUNO", "integer"),
                   Field("NOME_DOCENTE", "string"),
                   Field("PAPEL_DOCENTE", "string"),
                   Field("ANO", "integer"),
                   Field("PERIODO", "integer"),
                   Field("PERIODO_ITEM", "integer"),
                   Field("DESCRICAO", "string"),
                   Field("SITUACAO_ITEM", "integer"),
                   Field("COD_TURMA", "string"),
                   Field("HORA_INICIO_AULA", "time"),
                   Field("HORA_FIM_AULA", "time"),
                   Field("DIA_DA_AULA", "string"),
                   Field("TIPO_DE_AULA", "string"),
                   primarykey=['ID_ALUNO', 'ANO', 'PERIODO', 'HORA_INICIO_AULA' ],
                   migrate=False
                   )