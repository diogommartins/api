dbSie.define_table(
    'V_COEF_REND_ACAD',
    Field('ID_ALUNO', 'integer'),
    Field('ID_CURSO_ALUNO', 'integer'),
    Field('COEFICIENTE', 'float'),
    Field('FORMA_EVASAO_ITEM', 'integer'),
    Field('MATR_ALUNO', 'string'),
    Field('PERIODO_ATUAL', 'integer'),
    primarykey=['ID_ALUNO'],
    migrate=False,
    rname='DBSM.V_COEF_REND_ACAD'
)