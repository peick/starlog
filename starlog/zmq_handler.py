import os
import threading
import traceback
from logging import makeLogRecord

import zmq

from .base_handler import BaseMultiprocessHandler
from .debug import get_debug_logger
from .serializer import record_to_dict


_log = get_debug_logger('starlog.debug.queue_handler')


class ZmqPushPullHandler(BaseMultiprocessHandler):
    def __init__(self, address='tcp://127.0.0.1:5557',
                 logger='starlog.logsink'):
        BaseMultiprocessHandler.__init__(self, logger)

        self._address = address
        self._async_listener = self._start_listener_thread(address)

        # for child processes
        self._pid = None

    def _start_listener_thread(self, address):
        _log.info('MultiprocessHandler._start_listener_thread')
        listener = ZmqPullListenerThread(address, self)
        listener.start()
        return listener

    def forward_to_master(self, record):
        socket = self._get_socket()
        record_dict = record_to_dict(record, self)
        socket.send_json(record_dict)

    def _get_socket(self):
        pid = os.getpid()

        if self._pid != pid:
            # pid is None: new child forked from master
            # pid != os.getpid(): new child forked from other child
            self._bind_to_socket()
            self._pid = pid

        return self._socket

    def _bind_to_socket(self):
        context = zmq.Context()
        socket = context.socket(zmq.PUSH)
        socket.connect(self._address)

        self._socket = socket

    def __del__(self):
        _log.info('MultiprocessHandler.__del__ for %s', self)

        if not self._is_master_process():
            self.close()

        listener_thread = self._async_listener
        if listener_thread is None:
            return

        listener_thread.shutdown()
        listener_thread.join()

        self.close()

    def close(self):
        BaseMultiprocessHandler.close(self)
        try:
            socket = self._socket
        except AttributeError:
            return
        else:
            if socket is not None:
                socket.close()
                self._socket = None


class ZmqListenerThread(threading.Thread):
    def __init__(self, address, handler, *args, **kwargs):
        super(ZmqListenerThread, self).__init__(*args, **kwargs)
        self.setDaemon(True)

        self._address = address
        self._handler = handler
        self._running = True

    def run(self):
        socket = self._bind_to_socket(self._address)

        try:
            while self._running:
                record_dict = socket.recv_json()
                self._process_record(record_dict)
        except Exception:
            _log.warn('exception in %s.run: %s',
                      self.__class__.__name__, traceback.format_exc())

        _log.info('%s stopped', self.__class__.__name__)

    def _bind_to_socket(self, address):
        raise NotImplementedError()

    def _process_record(self, record_dict):
        record = makeLogRecord(record_dict)
        self._handler.forward_to_sink(record)

    def shutdown(self):
        self._running = False


class ZmqPullListenerThread(ZmqListenerThread):
    def _bind_to_socket(self, address):
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind(self._address)
        return socket
