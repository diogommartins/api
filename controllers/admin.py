# coding=utf-8
from api.key import APIKey


@auth.requires_membership('Desenvolvedor')
def refresh_cache():
    endpoints_definer.refresh_cache()
    load_endpoints(write_models=True)

    return dict()


@auth.requires_membership('Desenvolvedor')
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


@auth.requires_membership('Desenvolvedor')
def user():
    grid = SQLFORM.grid(
        query=db.auth_user,
        editable=True,
        deletable=False,
        csv=False
    )
    return dict(grid=grid)


@auth.requires_membership('Desenvolvedor')
def membership():
    grid = SQLFORM.grid(
        query=db.auth_membership,
        editable=False,
        deletable=False,
        details=False,
        csv=False
    )
    return dict(grid=grid)


@auth.requires_membership('Desenvolvedor')
def permissions_endpoints():
    endpoints = sorted(datasource.tables)
    db.api_group_permissions.table_name.requires = IS_IN_SET(endpoints)
    grid = SQLFORM.grid(
        query=db.api_group_permissions,
        editable=False,
        deletable=False,
        csv=False
    )
    return dict(grid=grid)


@auth.requires_membership('Desenvolvedor')
def permissions_procedures():
    return dict()
