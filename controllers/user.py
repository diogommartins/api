# -*- coding: utf-8 -*-

@auth.requires_login()
def createKeyAuth():
    from APIKey import APIKey
    apiKey = APIKey()
    currentAPIKey = APIKey.getCurrentActiveKeyForUser( auth.user.id )

    #Se ainda não existir uma chave válida
    if not currentAPIKey:
        currentAPIKey = apiKey.genarateNewKeyForUser( auth.user.id )

    form = FORM(
                "Sua chave de API (API KEY) é: ",
                INPUT( _value=currentAPIKey, _name="apiKey", _size='600', _readonly=True ),
                INPUT( _value="Gerar nova Chave", _type="submit" )
                )

    if form.process().accepted:
        apiKey.genarateNewKeyForUser( auth.user.id )
        redirect(request.referer, client_side=True)

    return dict(form=form)

def authHistory():
    grid = SQLFORM.grid( ( db.api_auth.user_id==auth.user.id ),
                         fields= (db.api_auth.auth_key, db.api_auth.dt_creation, db.api_auth.active),
                         deletable=False,
                         create=False,
                         editable=False,
                         csv=False )

    return dict(grid=grid)

def createKeyGuest():
    pass