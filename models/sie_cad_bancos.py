# coding=utf-8
dbSie.define_table(
    'CAD_BANCOS',
    Field('ID_BANCO', 'integer'),
    Field('COD_BANCO', 'string'),
    Field('DV_BANCO', 'string'),
    Field('NOME_BANCO', 'string'),
    Field('LOGO_BANCO', 'blob'),
    Field('COD_OPERADOR', 'integer'),
    Field('DT_ALTERACAO', 'date'),
    Field('HR_ALTERACAO', 'time'),
    Field('CONCORRENCIA', 'integer'),
    Field('ID_EVENTO_BANCO', 'integer'),
    Field('ENDERECO_FISICO', 'string'),
    primarykey=['ID_BANCO'],
    migrate=False
    )