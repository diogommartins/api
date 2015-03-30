dbSie.define_table(
    'V_PROCESSOS_ASSUNTOS_QTD',
    Field('DESCR_ASSUNTO'),
    Field('COD_ESTRUTURADO'),
    Field('TOTAL', 'integer'),
    migrate=False,
    primarykey=['COD_ESTRUTURADO'],
    rname='DBSM.V_PROCESSOS_ASSUNTOS_QTD'
)