# coding=utf-8
from api.key import Key


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
        api_key = Key(db)
        current_key = Key.get_current_active_key_for_user(form.vars.user_id)

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
    return _permissions_grid(db.api_group_permissions, 'table_name', sorted(datasource.tables))


@auth.requires_membership('Desenvolvedor')
def permissions_procedures():
    return _permissions_grid(db.api_procedure_permissions, 'name', sorted(PROCEDURES.keys()))


def _permissions_grid(table, field, options):
    table[field].requires = IS_IN_SET(options)
    grid = SQLFORM.grid(
        query=table,
        editable=False,
        deletable=False,
        csv=False
    )

    return dict(grid=grid)
