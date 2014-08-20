# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


def index():
    from TableBeautify import *
    response.title = 'API UNIRIO'

    tableBeautify = TableBeautify( dbSie.tables )

    accessPermissions = db( db.auth_group ).select( db.auth_group.role ).as_list()
    avaiableData = dbSie.tables
    avaiableFields = []
    for table in avaiableData:
        avaiableFields.append( {table : dbSie[table].fields} )

    return dict(
                accessPermissions=accessPermissions,
                avaiableData = avaiableData,
                avaiableFields = avaiableFields,
                tabelas = tableBeautify.beautifyDatabaseTables()
                )

#página com os créditos
def sobre():
    pass

@request.restful()
def rest():
    response.view = 'generic.'+request.extension
    def GET(*args,**vars):
        patterns = [
                    "/ALUNOS[ALUNOS]",
                    "/ALUNOS/{ALUNOS.ID_ALUNO}",
                    "/ALUNOS/ID-ALUNO/{ALUNOS.ID_ALUNO}/:field",
                    ':auto[ALUNOS]',
                    ':auto[CURSOS]',
                    ':auto[CURSOS_ALUNOS]',
                    ':auto[DISCIPLINAS]',
                    ':auto[TAB_ESTRUTURADA]',
                    ':auto[VERSOES_CURSOS]'
                    ]
        parser = dbSie.parse_as_rest(patterns,args,vars)
        if parser.status == 200:
            return dict(content=parser.response)
        else:
            raise HTTP(parser.status,parser.error)
    return locals()

@request.restful()
def alunos():
    response.view = 'generic.'+request.extension
    def GET(*args,**vars):
        patterns = [
                    "/ALUNOS[ALUNOS]",
                    "/ALUNOS/ID-ALUNO/{ALUNOS.ID_ALUNO}",
                    "/ALUNOS/ID-ALUNO/{ALUNOS.ID_ALUNO}/:field",
                    "/ALUNOS/ETNIA-ITEM/{ALUNOS.ETNIA_ITEM}/",
                    "/ALUNOS/ETNIA-ITEM/{ALUNOS.ETNIA_ITEM}/:field",
                    ]
        parser = dbSie.parse_as_rest(patterns,args,vars)
        if parser.status == 200:
            return dict(content=parser.response)
        else:
            raise HTTP(parser.status,parser.error)
    return locals()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
