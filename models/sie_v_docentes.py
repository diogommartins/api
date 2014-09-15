# -*- coding: utf-8 -*-
dbSie.define_table("V_DOCENTES",
                   Field('ID_CONTRATO_RH', 'integer'),
                   Field('MATR_EXTERNA', 'integer'),
                   Field('NOME_DOCENTE', 'string'),
                   Field('ID_LOT_EXERCICIO', 'integer'),
                   Field('ID_CARGO', 'integer'),
                   Field('SITUACAO_ITEM', 'integer'),
                   Field('SITUACAO_TAB', 'integer'),
                   Field('JORNADA_TRAB_TAB', 'integer'),
                   Field('JORNADA_TRAB_ITEM', 'integer'),
                   Field('CONCORRENCIA', 'integer'),
                   Field('CPF_MASCARA', 'string'),
                   Field('CPF', 'string'),
                   migrate=False)