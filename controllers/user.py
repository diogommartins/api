# -*- coding: utf-8 -*-
from api.key import APIKey


@auth.requires_login()
def index():
    apiKeysGrid = SQLFORM.grid((db.api_auth.user_id == auth.user.id ),
                               fields=(db.api_auth.auth_key, db.api_auth.dt_creation, db.api_auth.active),
                               deletable=False,
                               create=False,
                               editable=False,
                               searchable=False,
                               maxtextlength=160,
                               csv=False)

    return dict(apiKeysGrid=apiKeysGrid)


@auth.requires_login()
def create_user_key():
    api_key = APIKey(db)
    current_key = APIKey.get_current_active_key_for_user(auth.user.id)

    if not current_key:
        current_key = api_key.genarate_new_key_for_user(auth.user.id)

    form = FORM(
        "Sua chave de API (API KEY) é: ",
        INPUT(_value=current_key, _name="apiKey", _size='600', _readonly=True),
        INPUT(_value="Gerar nova Chave", _type="submit")
    )

    if form.process().accepted:
        api_key.genarate_new_key_for_user(auth.user.id)
        redirect(URL('user', 'index'), client_side=True)

    return dict(form=form)


@auth.requires(auth.has_membership('Desenvolvedor'))
def create_system_key():
    key = ''

    # Retorna todos os usuários cadastrados como sistemas
    sistemas = db((db.auth_user.id == db.auth_membership.user_id) & (
        db.auth_membership.group_id == 4)).select(db.auth_user.id, db.auth_user.first_name)

    form = FORM(
        SELECT([OPTION(s.first_name, _value=s.id) for s in sistemas], _name='user_id'),
        INPUT(_value="Gerar nova Chave", _type="submit")
    )

    if form.validate():
        api_key = APIKey(db)
        current_key = APIKey.get_current_active_key_for_user(form.vars.user_id)

        # Se ainda não existir uma chave válida
        if not current_key:
            current_key = api_key.genarate_new_key_for_user(form.vars.user_id)
            response.flash = "Nova chave gerada"
        else:
            response.flash = "Uma chave já existe para sistema " + form.vars.user_id

        key = current_key

    return dict(form=form, key=key)


@auth.requires(auth.has_membership('Desenvolvedor'))
def user():
    grid = SQLFORM.grid(
        query=db.auth_user,
        editable=True,
        deletable=False,
        csv=False
    )
    return dict(grid=grid)


@auth.requires(auth.has_membership('Desenvolvedor'))
def membership():
    grid = SQLFORM.grid(
        query=db.auth_membership,
        editable=False,
        deletable=False,
        details=False,
        csv=False
    )
    return dict(grid=grid)


@auth.requires(auth.has_membership('Desenvolvedor'))
def permissions():
    endpoints = sorted(datasource.tables)
    db.api_group_permissions.table_name.requires = IS_IN_SET(endpoints)
    grid = SQLFORM.grid(
        query=db.api_group_permissions,
        editable=False,
        deletable=False,
        csv=False
    )
    return dict(grid=grid)
