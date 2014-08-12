# -*- coding: utf-8 -*-
from gluon.dal import Field
if request.env.web2py_runtime_gae:
    db = DAL('gae')
    session.connect(request, response, db = db)
else:
    from gluon import current
    current.dbSie = dbSie
    current.db = db


#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import *
from gluon.contrib.login_methods.ldap_auth import ldap_auth

mail = Mail()                                  # mailer
auth = Auth(globals(),db)                      # authentication/authorization
crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()

mail.settings.server = 'logging' or 'smtp.gmail.com:587'  # your SMTP server
mail.settings.sender = 'you@gmail.com'         # your email
mail.settings.login = 'username:password'      # your credentials or None

## create all tables needed by auth if not custom tables
auth.define_tables(username=True)
auth.settings.create_user_groups=False

auth.settings.login_methods=[ldap_auth(mode='uid',server='10.224.16.100', base_dn='ou=people,dc=unirio,dc=br')]
auth.settings.actions_disabled=['register','retrieve_username','profile','lost_password']
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
                Field("type_id", db.api_request_type), # Está aqui porque o usuário pode estar em mais de um grupo
                Field("dt_request", "datetime"),
                Field("url", "string"),
                Field("auth_key", db.api_auth, label="Key ID"),
                Field("ip", "string")
                )