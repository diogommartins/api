dbSie.define_table(
    'V_BOLSISTAS_MONITORIA',
    Field('AGENCIA'),
    Field('COD_BANCO'),
    Field('CONTA_CORRENTE'),
    Field('CPF'),
    Field('DESC_BANCO'),
    Field('ID_BOLSISTA', 'integer'),
    Field('ID_PROJETO', 'integer'),
    Field('MATRICULA', 'integer'),
    Field('PARTICIPANTE', 'integer'),
    migrate=False,
    rname='DBSM.V_BOLSISTAS_MONITORIA'
)