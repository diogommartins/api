dbSie.define_table(
    'V_ALUNOS_ATIVOS',
    Field('CPF', 'string'),
    Field('CPF_SEM_MASCARA', 'string'),
    Field('CURSO', 'string'),
    Field('DATANASCIMENTO', 'date'),
    Field('ID_ALUNO', 'integer'),
    Field('ID_CURSO_ALUNO', 'integer'),
    Field('ID_PESSOA', 'integer'),
    Field('MATRICULA', 'string'),
    Field('NOME', 'string'),
    Field('PERIODO', 'integer'),
    Field('TIPO_DE_ALUNO', 'string'),
    primarykey=['ID_ALUNO'],
    migrate=False,
    rname='DBSM.V_ALUNOS_ATIVOS'
    )