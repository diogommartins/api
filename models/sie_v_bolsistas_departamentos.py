dbSie.define_table(
    'V_BOLSISTAS_DEPARTAMENTOS',
    Field('ID_UNIDADE', 'integer'),
    Field('NOME_UNIDADE'),
    Field('TOTAL', 'integer'),
    migrate=False,
    primarykey=['ID_UNIDADE'],
    rname='DBSM.V_BOLSISTAS_DEPARTAMENTOS'
)