# -*- coding: utf-8 -*-
from AESCipher import AESCipher
from gluon import current
from datetime import datetime


class APIKey():
    def __init__(self, hash=None):
        self.hash = hash
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.auth_key = self.authKeyForHash()


    # Returns the user_id of the API KEY owner
    def owner(self):
        authKeyOwner = current.db(current.db.api_auth.auth_key == self.hash).select(current.db.api_auth.user_id).first()
        if authKeyOwner:
            return authKeyOwner.user_id

    def _makeHash(self, username):
        aes = AESCipher()
        return aes.encrypt(username + self.timestamp)

    # Gera uma nova chave valida para o usuario, inutiliza a anterior e retorna a mesma
    def genarateNewKeyForUser(self, user_id):
        apiUser = current.db(current.db.auth_user.id == user_id).select(current.db.auth_user.username).first()
        if apiUser:
            newKey = self._makeHash(apiUser.username)
            previousApiKey = current.db(
                (current.db.api_auth.user_id == user_id) &
                (current.db.api_auth.active == True)
            ).select().first()
            # Se existir, invalida chave anterior
            if previousApiKey:
                previousApiKey.update_record(active=False)
            # Insere nova chave no banco. Obs.:Não deveria estar funcionando sem o commit, mas...
            current.db.api_auth.insert(
                auth_key=newKey,
                user_id=user_id,
                dt_creation=self.timestamp,
                active=True
            )
            return newKey

    @staticmethod
    def getCurrentActiveKeyForUser(user_id):
        api_auth = current.db(
            (current.db.api_auth.user_id == user_id) & (current.db.api_auth.active == True)).select().first()
        if api_auth:
            return api_auth.auth_key

    def authKeyForHash(self):
        auth_key = current.db(
            (current.db.api_auth.auth_key == self.hash)
            & (current.db.api_auth.active == True)
        ).select().first()
        return auth_key if auth_key else None

    def isValidKey(self):
        return True if self.auth_key else False

    @staticmethod
    def isValidKey(hash):
        auth_key = current.db(
            (current.db.api_auth.auth_key == hash)
            & (current.db.api_auth.active == True)
        ).select(current.db.api_auth.id).first()

        return auth_key if auth_key else False

    @staticmethod
    def checkKeyForUser(apiKey, user_id):
        return current.db(
            (current.db.api_auth.auth_key == apiKey) & (current.db.api_auth.user_id == user_id)).select().first()
