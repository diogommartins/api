# coding=utf-8
import simplejson
from .exceptions import ProcedureDatasetException
from procedures import Procedure
from datetime import datetime
import time
from gluon.contrib.websocket_messaging import websocket_send
import threading


class ProcedureWorker(object):
    def __init__(self, db, datasource, name, websocket, sleep_time=3):
        """
        :type db: gluon.dal.DAL
        :param db: The DAL where api_procedure_queue table is defined
        :type websocket: dict
        :param websocket: Dictionary containing websocket parameters and the keys `uri` and `password`
        :type sleep_time: int or float
        :param sleep_time: Time in seconds, to wait between checking for new itens on queue
        :type datasource: gluon.dal.DAL
        :type name: str
        """
        self.db = db
        self.datasource = datasource
        self.name = name
        self.procedure = Procedure(self.name, self.datasource)
        self.ws = websocket
        self.sleep_time = sleep_time
        self.queue = []
        self.__running = False
        self.thread = None

    def get_entries(self):
        """
        Fetches all queue entries of `self.procedure` type that weren't already processed and update the queue list
        """
        # todo Não deveria ser necessário reconectar, mas após o final de uma requisição, o web2py fecha todas
        # as conexões. Ver : gluon.main l468
        if not self.db._adapter.connection:
            self.db._adapter.reconnect()

        return self.db((self.db.api_procedure_queue.dt_conclusion == None)
                       & (self.db.api_procedure_queue.name == self.name)).select()

    def _update_entry(self, entry):
        """
        Changes an entry status to finished
        :type entry: gluon.dal.Row
        """
        entry.update_record(dt_conclusion=datetime.now())

    def __thread_is_alive(self, thread):
        for t in threading.enumerate():
            if t.name == thread.name:
                return True
        return False

    def start(self):
        """
        Detach and start a new thread
        """
        self.thread = threading.Thread(target=self.work, name=self.name)
        if not self.__thread_is_alive(self.thread):
            self.__running = True
            self.thread.start()

    def stop(self):
        """
        Sets running to False, which will end the thread target callable main loop, causing it to end
        """
        self.__running = False

    def _notify_websocket_server(self, entry, message):
        """

        :type entry: gluon.dal.Row
        :param message: a json serializable
        """
        notification_group = entry.ws_group or self.name
        websocket_send("http://%s:%s" % (self.ws['host'], self.ws['port']), simplejson.dumps(message), self.ws['password'], notification_group)

    def work(self):
        while self.__running:
            for entry in self.queue:
                dataset = simplejson.loads(entry.json_data)
                try:
                    message = self.procedure.perform_work(dataset)
                    entry.update_record(
                        did_finish_correctly=True,
                        dt_conclusion=datetime.now(),
                        resulting_dataset=message
                    )
                except ProcedureDatasetException as e:
                    entry.update_record(
                        did_finish_correctly=False,
                        status_description=e.cause,
                        dt_conclusion=datetime.now(),
                        resulting_dataset=e.dataset
                    )

                    message = e.dataset

                    if entry.result_fields:
                        message = {k: v for k, v in e.dataset if k in entry.result_fields}

                    # todo Que erro deve ser enviado ? Deve ser enviado o nome da exception tb ?
                    message.update(error=str(e.cause))
                finally:
                    self.db.commit()
                self._notify_websocket_server(entry, message)

            time.sleep(self.sleep_time)
            self.queue = self.get_entries()

