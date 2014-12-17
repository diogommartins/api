# -*- coding: utf-8 -*-
dbSie.define_table("V_CURSOS_DISCIPLINAS",
                   Field('NOME_CURSO', 'string'),
                   Field('NOME_CURSO_DIPLOMA', 'string'),
                   Field('NIVEL_CURSO_ITEM', 'integer'),
                   Field('TIPO_CURSO_ITEM', 'integer'),
                   Field('COD_DISCIPLINA', 'string'),
                   Field('NOME_DISCIPLINA', 'string'),
                   Field('OBRIGATORIA', 'string', length=1), #S-Sim, N-Nao
                   Field('ID_DISCIPLINA', 'integer'),
                   Field('ID_DISC_CURRIC', 'integer'),
                   Field('ID_ESTRUTURA_CUR', 'integer'),
                   Field('ID_VERSAO_CURSO', 'integer'),
                   Field('ID_CURSO', 'integer'),
                   Field('ID_UNIDADE', 'integer'),
                   primarykey=['ID_DISC_CURRIC'],
                   migrate=False,
                   rname="DBSM.V_CURSOS_DISCIPLINAS")