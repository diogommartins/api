# -*- coding: utf-8 -*-
from gluon import current
from gluon.contrib.login_methods.ldap_auth import ldap_auth
from gluon.tools import Auth, Service, Crud
from datetime import datetime

# Dummy code to enable code completion in IDE's. Can be removed at production apps
if 0:
    datasource = DAL()

current.datasource = datasource
current.db = db

auth = Auth(globals(), db)  # authentication/authorization
auth.settings.login_methods = [ldap_auth(mode='uid', server='ldap.unirio.br', base_dn='ou=people,dc=unirio,dc=br')]

crud = Crud(globals(), db)  # for CRUD helpers using auth
service = Service(globals())  # for json, xml, jsonrpc, xmlrpc, amfrpc

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

db.define_table("api_methods",
                Field("http_method", "string")
)

db.define_table("api_request",
                Field("dt_request", "datetime"),
                Field("endpoint", "string"),
                Field("parameters", "text"),
                Field("auth_key", db.api_auth, label="Key ID"),
                Field("ip", "string"),
                Field("http_method", db.api_methods)
)

db.define_table("api_group_permissions",
                Field("table_name", "string"),
                Field("column_name", "string", notnull=False),
                Field("http_method", db.api_methods),
                Field("all_columns", "boolean"),
                Field("group_id", db.auth_group),
                Field("unique_validator", unique=True,
                      compute=lambda r: r.table_name + r.column_name + str(r.http_method) + str(r.group_id))
)

db.define_table("api_procedure_queue",
                Field("name"),
                Field("json_data", "json"),
                Field("dt_creation", "datetime", default=datetime.now()),
                Field("dt_conclusion", "datetime"),
                Field("ws_group", label='Websocket group to notify'),
                Field("did_finish_correctly", "boolean", label="Job finished as expected"),
                Field("status_description", length=1014),
                Field("resulting_dataset", "json")
                )

db.api_group_permissions.http_method.requires = IS_IN_DB(db, db.api_methods.id, '%(http_method)s')