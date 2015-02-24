# coding=utf-8
dbSie.define_table(
    'CAD_AGENCIAS',
    Field('ID_AGENCIA', 'integer'),
    Field('ID_BANCO', 'integer'),
    Field('COD_AGENCIA'),
    Field('DV_AGENCIA'),
    Field('NOME_AGENCIA'),
    Field('COD_OPERADOR', 'integer'),
    Field('DT_ALTERACAO', 'date'),
    Field('HR_ALTERACAO', 'time'),
    Field('CONCORRENCIA', 'integer'),
    Field('ENDERECO_FISICO'),
    primarykey=['ID_AGENCIA'],
    migrate=False
)