dbSie.define_table(
    'V_BOLSISTAS_ATIVOS_DADOS',
    Field('BOLSISTA'),
    Field('COORDENADOR'),
    Field('ID_BOLSISTA', 'integer'),
    Field('ID_PROJETO', 'integer'),
    Field('TITULO'),
    Field('NOME_DISCIPLINA'),
    Field('NOME_UNIDADE'),
    Field('NUM_PROCESSO'),
    Field('VL_BOLSA', 'float'),
    migrate=False,
    primarykey=['ID_BOLSISTA'],
    rname='DBSM.V_BOLSISTAS_ATIVOS_DADOS'
)