# coding=utf-8
import simplejson
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
        callable_procedure = Procedure()(self.name)
        self.procedure = callable_procedure(datasource=self.datasource)
        self.ws = websocket
        self.sleep_time = sleep_time
        self.queue = []
        self.__running = False
        self.thread = None

    def update_queue(self):
        """
        Fetches all queue entries of `self.procedure` type that weren't already processed and update the queue list
        """
        self.queue = self.db(
            (self.db.api_procedure_queue.dt_conclusion == None)
            & (self.db.api_procedure_queue.name == self.name)).select()

    def _update_entry(self, entry):
        """
        Changes an entry status to finished
        :type entry: gluon.dal.Row
        """
        entry.update_record(dt_conclusion=datetime.now())

    def start(self):
        """
        Detach and start a new thread
        """
        self.thread = threading.Thread(target=self.work, name=self.name)
        if not self.thread.isAlive():
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
        websocket_send(self.ws['uri'], simplejson.dumps(message), self.ws['password'], notification_group)

    def work(self):
        while self.__running:
            for entry in self.queue:
                dataset = simplejson.loads(entry.json_data)
                message = self.procedure.perform_work(dataset)
                self._update_entry(entry)
                self._notify_websocket_server(entry, message)

            time.sleep(self.sleep_time)
            self.update_queue()
