# -*- coding: utf-8 -*-
from gluon.dal import Field
from gluon import current
from gluon.tools import *

current.dbSie = dbSie
current.db = db

mail = Mail()  # mailer
auth = Auth(globals(), db)  # authentication/authorization
crud = Crud(globals(), db)  # for CRUD helpers using auth
service = Service(globals())  # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()


if not request.is_local:
    from gluon.contrib.login_methods.ldap_auth import ldap_auth

    auth.settings.login_methods = [ldap_auth(mode='uid', server='ldap.unirio.br', base_dn='ou=people,dc=unirio,dc=br')]

# # create all tables needed by auth if not custom tables
auth.define_tables(username=True)
auth.settings.everybody_group_id = 6
auth.settings.create_user_groups = False

auth.settings.actions_disabled = [
    'register',
    'retrieve_username',
    'profile',
    'lost_password'
]
db.auth_user.username.label = 'CPF'

db.define_table("api_request_type",
                Field("group_id", db.auth_group),
                Field("max_requests", "integer"),
                Field("max_entries", "integer")
)

db.define_table("api_auth",
                Field("auth_key", "string"),
                Field("user_id", db.auth_user),
                Field("dt_creation", "datetime"),
                Field("active", "boolean")
)

db.define_table("api_request",
                Field("type_id", db.api_request_type),  # Está aqui porque o usuário pode estar em mais de um grupo
                Field("dt_request", "datetime"),
                Field("url", "string"),
                Field("auth_key", db.api_auth, label="Key ID"),
                Field("ip", "string")
)

db.define_table("api_methods",
                Field("http_method", "string")
)

#===============================================================================
#
# Field table_name        Tabela modelada pela qual será restringida
# Field column_name       Coluna da tabela
# Field all_columns      Caso a restrição seja aplicável a todas as colunas, recebe True
# Field group_id            auth_user_group de uma API KEY
#
# Ex:
#    table_name    = PESSOAS
#    column_name   = NOME_PESSOA
#    group_id      = Aluno
#
#
#
#    Na tabela PESSOAS, o campo NOME_PESSOA tem restrição de acesso na qual
#    usuários ['Aluno', 'Sistema Convidado', 'Convidado'] não podem acessar e
#    ['Professor', 'Servidor', 'Sistema', 'Desenvolvedor'] podem.
#
#===============================================================================
db.define_table("api_group_permissions",
                Field("table_name", "string"),
                Field("column_name", "string", notnull=False),
                Field("http_method", db.api_methods),
                Field("all_columns", "boolean"),
                Field("group_id", db.auth_group),
                Field("unique_validator", unique=True,
                      compute=lambda r: r.table_name + r.column_name + str(r.http_method) + str(r.group_id))
)

db.api_group_permissions.http_method.requires = IS_IN_DB(db, db.api_methods.id, '%(http_method)s')
