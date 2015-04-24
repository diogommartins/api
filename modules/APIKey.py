# -*- coding: utf-8 -*-
from datetime import datetime
from AESCipher import AESCipher
from gluon import current


class APIKey(object):
    def __init__(self, db, hash=None):
        self.db = db
        self.cache = (current.cache.ram, 86400)
        self.hash = hash
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.auth = self.authForHash(hash)
        if self.auth:
            self.max_request, self.max_entries = self.requestLimits()

    def owner(self):
        """
        Retorna o user_id do dono da API Key

        :rtype : int
        :return:
        """
        authKeyOwner = self.db(self.db.api_auth.auth_key == self.hash).select(self.db.api_auth.user_id).first()
        if authKeyOwner:
            return authKeyOwner.user_id

    def _makeHash(self, username):
        """
        Método utilizado para criar um novo hash a ser utilizado como API Key para o usuário

        :type username: str
        :rtype : str
        """
        aes = AESCipher()
        return aes.encrypt(username + self.timestamp)

    def genarateNewKeyForUser(self, user_id):
        """
        Gera uma nova chave valida para o usuário, inutiliza a anterior e retorna a nova chave criada.

        :rtype : str
        :param user_id:
        :return:
        """
        user = self.db(current.db.auth_user.id == user_id).select(self.db.auth_user.username).first()
        if user:
            newKey = self._makeHash(user.username)
            previousApiKey = current.db(
                (self.db.api_auth.user_id == user_id) &
                (self.db.api_auth.active == True)
            ).select().first()
            if previousApiKey:
                previousApiKey.update_record(active=False)
            # Insere nova chave no banco.
            # TODO: Não deveria estar funcionando sem o commit, mas...
            self.db.api_auth.insert(
                auth_key=newKey,
                user_id=user_id,
                dt_creation=self.timestamp,
                active=True
            )
            return newKey

    @staticmethod
    def getCurrentActiveKeyForUser(user_id):
        """
        Dado um usuário válido cadastrado em um grupo, e com uma chave válida, o método retorna a chave ativa no momento

        :rtype : str
        :param user_id: O ID de um usuário na tabela auth_user
        :return: O hash de uma chave válida
        """
        api_auth = current.db(
            (current.db.api_auth.user_id == user_id) & (current.db.api_auth.active == True)).select().first()
        if api_auth:
            return api_auth.auth_key

    def authForHash(self, hash):
        """
        Dado um determinado hash, o método retornará a entrada da tabela api_auth correspondente,
        caso seja um hash válido e a chave esteja ativa.

        :rtype : gluon.DAL.Row
        :return: Uma entrada da tabela api_auth
        """
        return self.db(
            (self.db.api_auth.auth_key == hash)
            & (self.db.api_auth.active == True)
        ).select(cache=self.cache, cacheable=True).first()

    def requestLimits(self):
        limits = self.db(
            (self.db.auth_membership.user_id == self.auth.user_id)
            & (self.db.auth_membership.group_id == current.db.api_request_type.group_id)
        ).select(self.db.api_request_type.max_requests,
                 current.db.api_request_type.max_entries,
                 cache=self.cache, cacheable=True).first()

        return limits.max_requests, limits.max_entries

    @staticmethod
    def isValidKey(hash):
        """
        Método utilizado para validar se um hash é válido como API Key

        :rtype : bool
        :param hash: O hash de uma API Key a ser vaidada
        :return: Uma entrada da tabela api_auth
        """
        return True if current.db(
            (current.db.api_auth.auth_key == hash)
            & (current.db.api_auth.active == True)
        ).select(current.db.api_auth.id).first() else False

    @staticmethod
    def checkKeyForUser(apiKey, user_id):
        return current.db(
            (current.db.api_auth.auth_key == apiKey) & (current.db.api_auth.user_id == user_id)).select().first()
