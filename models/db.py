# -*- coding: utf-8 -*-
if request.env.web2py_runtime_gae:
    db = DAL('gae')
    session.connect(request, response, db = db)
else:
    from gluon import current
    current.dbSie = dbSie


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
db.auth_user.username.label = 'CPF'
