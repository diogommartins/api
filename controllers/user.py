# -*- coding: utf-8 -*-
from api.key import Key


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
    api_key = Key(db)
    current_key = Key.get_current_active_key_for_user(auth.user.id)

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
