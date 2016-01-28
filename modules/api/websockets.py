# coding=utf-8
from gluon.contrib.websocket_messaging import websocket_send
from gluon.serializers import json
from gluon import current
from .operations import APIOperationObserver


class WebsocketNotificator(APIOperationObserver):

    def __init__(self, verbose=True):
        assert current.ws_server

        self.host = current.ws_server['host']
        self.port = current.ws_server['port']
        self.password = current.ws_server['password']
        self.verbose = verbose

    def _notify_clients(self, message, group='default'):
        try:
            websocket_send("http://%s:%s" % (self.host, self.port), json(message), self.password, group)
        except IOError as e:
            if self.verbose:
                print("{notifier}: Unable to notify clients \"{exception}\". "
                      "The server is up and running? Follow the instructions "
                      "at \"gluon/contrib/websocket_messaging.py\"".format(notifier=self.__class__.__name__,
                                                                           exception=e.strerror))

    def did_finish_successfully(self, sender, parameters):
        message = parameters.copy()
        message['action'] = sender.__class__.__name__
        message['status'] = 'success'

        self._notify_clients(message, sender.endpoint)

    def did_finish_with_error(self, sender, parameters, error):
        message = parameters.copy()
        message['action'] = sender.__class__.__name__
        message['status'] = 'error'
        # todo: Não deve ser mandado de fato a nenhum cliente e deve ter outra forma em uma versão de produção
        message['cause'] = str(error)

        self._notify_clients(message, sender.endpoint)
