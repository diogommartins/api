dbSie.define_table(
    'V_BOLSISTAS_DADOS_BANCARIOS',
    Field('ID_BOLSISTA', 'integer'),
    Field('ID_CURSO_ALUNO', 'integer'),
    Field('COD_BANCO'),
    Field('DESC_BANCO'),
    Field('AGENCIA'),
    Field('CONTA_CORRENTE'),
    migrate=False,
    primarykey=['ID_BOLSISTA'],
    rname='DBSM.V_BOLSISTAS_DADOS_BANCARIOS'
)