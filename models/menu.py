# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A("DTIC/UNIRIO",
                  _class="brand",_href="http://www.unirio.br/dtic")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Your Name <you@example.com>'
response.meta.description = 'a cool new app'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL('default', 'index'), []),
    (T('API Keys'), False, URL('user', 'index'), []),
    (T('Sobre'), False, URL('default', 'sobre'), [])
]

adminMenu = [('Administração', False, False,[
    ('Gerar nova chave de sistema', False, URL('user', 'createNewSystemKey')),
    ('Usuários', False, URL('user', 'user')),
    ('Gerenciar Grupos', False, URL('user', 'membership')),
])]


if auth.has_membership('Desenvolvedor'):
    response.menu += adminMenu

DEVELOPMENT_MENU = False

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources

if DEVELOPMENT_MENU: _()

if "auth" in locals(): auth.wikimenu()
