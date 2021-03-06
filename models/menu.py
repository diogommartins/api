# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A("DTIC/UNIRIO",
                  _class="brand",_href="http://www.unirio.br/dtic")
response.title = request.application.replace('_', ' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Diogo Magalhães Martins <diogo.martins@unirio.br>'
response.meta.description = 'RESTful API powered by Web2py framework'
response.meta.keywords = 'unirio, api, rest, json, dados abertos, opendata'
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

adminMenu = [
    ('Administração', False, False, (
        ('Atualizar definições', False, URL('admin', 'refresh_cache')),
        ('Gerar nova chave de sistema', False, URL('admin', 'create_system_key')),
        ('Usuários', False, URL('admin', 'user')),
        ('Gerenciar Grupos', False, URL('admin', 'membership')),
        ('Gerenciar Permissões de Endpoints', False, URL('admin', 'permissions_endpoints')),
        ('Gerenciar Permissões de Procedures', False, URL('admin', 'permissions_procedures')),
        ('Blacklist', False, URL('admin', 'blacklist'))
    ))
]


if auth.has_membership('Desenvolvedor'):
    response.menu += adminMenu

if "auth" in locals(): auth.wikimenu()
