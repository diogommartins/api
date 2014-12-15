# -*- coding: utf-8 -*-
dbSie.define_table("V_DISCIPLINAS",
                   Field('NOME_CURSO', 'string'),
                   Field('NOME_CURSO_DIPLOMA', 'string'),
                   Field('COD_ATIV_CURRIC', 'string'),
                   Field('NOME_ATIV_CURRIC', 'string'),
                   Field('OBRIGATORIA', 'string', length=1), #S-Sim, N-Nao
                   Field('ID_ATIV_CURRIC', 'integer'),
                   Field('ID_DISC_CURRIC', 'integer'),
                   Field('ID_ESTRUTURA_CUR', 'integer'),
                   Field('ID_VERSAO_CURSO', 'integer'),
                   Field('ID_CURSO', 'integer'),
                   Field('ID_UNIDADE', 'integer'),
                   primarykey=['ID_DISC_CURRIC'],
                   migrate=False,
                   rname="DBSM.V_DISCIPLINAS")