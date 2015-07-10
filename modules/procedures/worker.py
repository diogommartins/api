# coding=utf-8
import simplejson
from procedures import Procedure
from datetime import datetime, time
from gluon.contrib.websocket_messaging import websocket_send


class ProcedureWorker(object):
    def __init__(self, datasource, name, ws_server_uri, sleep_time):
        self.datasource = datasource
        callable_procedure = Procedure()(name)
        self.procedure = callable_procedure(datasource=self.datasource)
        self.ws_server_uri = ws_server_uri
        self.sleep_time = sleep_time
        self.queue = []

    def update_queue(self):
        """
        Pega todas as entradas da queue que não tenham dt_conclusão e sejam do tipo self.procedure

        """
        pass

    def _update_entry(self, entry):
        """
        Atualiza a entrada como concluída
        :param entry:
        """
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def _notify_websocket_server(self, entry, message):
        """
        :type entry: gluon.dal.Row
        :param message: a json serializable
        """
        websocket_send(self.ws_server_uri, simplejson.dumps(message))

    def work(self):
        for entry in self.queue:
            dataset = simplejson.loads(entry.json_data)
            message = self.procedure.perform_work(dataset)
            self._update_entry(entry)
            self._notify_websocket_server(entry, message)

        time.sleep(self.sleep_time)
