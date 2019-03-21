import errno
import os
import re
import threading
import traceback
from logging import makeLogRecord

import zmq

from .base_handler import BaseMultiprocessHandler
from .debug import get_debug_logger
from .serializer import record_to_dict
from .utils import retry, RetryAbortedByCheck


_log = get_debug_logger('starlog.debug.zmq_handler')


class BindFailedError(Exception):
    pass


def _requires_random_bind(address):
    if not address.startswith('tcp://'):
        return False

    if re.search(r':\d+$', address):
        return False
    else:
        return True


class RobustZmqSocket(object):
    UNRECOVERABLE_ERRORS = [
        # "Permission denied"
        errno.EACCES,
    ]

    DEFAULT_SOCKET_OPTIONS = {
        # set recv timeout
        'RCVTIMEO': 1000,
        'LINGER': 0,
    }

    def __init__(self, socket_type, address, backoff_factor=2.0, tries=8,
                 check=None, socket_options=DEFAULT_SOCKET_OPTIONS):
        # default: tries up to 4 minutes 15 seconds to bind / connect to
        # a socket
        self._socket_type = socket_type
        self._address = address

        self._context = None
        self._socket = None
        self._socket_options = socket_options

        self._retry_bind = retry(
            zmq.ZMQError,
            tries=tries,
            backoff_factor=backoff_factor,
            check=check,
            retry_log=self._log_bind_attempt)

        self._retry_connect = retry(
            zmq.ZMQError,
            tries=tries,
            backoff_factor=backoff_factor,
            check=check,
            retry_log=self._log_bind_attempt)

    def _obtain_context(self):
        if self._context is None:
            self._context = zmq.Context()

        return self._context

    def _log_bind_attempt(self, _trial, last_trial=False):
        if last_trial:
            _log.error('bind to %s failed. Aborting.', self._address)
        else:
            _log.warning('bind to %s failed. Retrying', self._address)

    def _log_connect_attempt(self, _trial, last_trial=False):
        if last_trial:
            _log.error('connect to %s failed. Aborting.', self._address)
        else:
            _log.warning('connect to %s failed. Retrying.', self._address)

    def bind(self):
        bind_with_retries = self._retry_bind(self._bind)
        bind_with_retries()

    def _bind(self):
        try:
            self.close_socket()
            context = self._obtain_context()
            self._socket = context.socket(self._socket_type)

            if _requires_random_bind(self._address):
                port = self._socket.bind_to_random_port(self._address)
                self._address = '%s:%d' % (self._address, port)
            else:
                self._socket.bind(self._address)

            self._set_socket_options()
        except zmq.ZMQError as error:
            if error.errno in self.UNRECOVERABLE_ERRORS:
                raise BindFailedError(str(error))

            raise

    def connect(self):
        connect_with_retries = self._retry_connect(self._connect)
        connect_with_retries()

    def _connect(self):
        self.close_socket()
        context = self._obtain_context()
        self._socket = context.socket(self._socket_type)
        self._socket.connect(self._address)

    def _set_socket_options(self):
        if not self._socket_options:
            return

        for option, value in self._socket_options.items():
            setattr(self._socket, option, value)

    def recv_json(self):
        try:
            return self._socket.recv_json()
        except zmq.ZMQError as error:
            if error.errno == errno.EAGAIN:
                # recv timeout
                return

            self.bind()

    def send_json(self, data):
        try:
            return self._socket.send_json(data)
        except zmq.ZMQError:
            self.connect()
            return self._socket.send_json(data)

    def close(self):
        """Close the zmq socket and destroy the zmq context.
        """
        self.close_socket()
        self.destroy_context()

    def destroy_context(self):
        """Destroy the zmq context.
        """
        if self._context is not None:
            if not self._context.closed:
                self._context.destroy()
            self._context = None

    def close_socket(self):
        """Close the zmq socket.
        """
        if self._socket is not None:
            if not self._socket.closed:
                self._socket.close()
            self._socket = None

    @property
    def address(self):
        assert not _requires_random_bind(self._address)
        return self._address


class ZmqHandler(BaseMultiprocessHandler):
    """The ZmqHandler creates a zmq connection between the main
    process and its children processes. The main process establishes a
    :py:const:`zmq.PULL` socket. Child processes sets up a :py:const:`zmq.PUSH`
    socket.

    All subprocesses sends messages to the zmq connection in the `emit`
    method. A background thread of the main process retrieves these messages
    and delegates them to the ``logger`` (default: ``starlog.sink``) in the
    main process.

    The ZmqHandler is expected to be set up by the main process.

    :param str address: the address of the connection which is passed to
        :py:meth:`zmq.Socket.connect` / :py:meth:`zmq.Socket.bind`.
        Examples: ``tcp://127.0.0.1:12345``, ``tcp://127.0.0.1``,
        ``ipc:///tmp/log.sock``. Omitting the port in a ``tcp://`` address
        will bind the socket to a random port.
    :param str logger: name of the logger where log records are send to in the
        main process.
    """

    def __init__(self, address='tcp://127.0.0.1:5557',
                 logger='starlog.logsink'):
        BaseMultiprocessHandler.__init__(self, logger)

        self._sender_socket_type = zmq.PUSH
        self._receiver_socket_type = zmq.PULL

        self._address = address
        self._async_listener = self._start_listener_thread(address)

        # for children processes
        self._pid = None

    def _start_listener_thread(self, address):
        _log.info('ZmqHandler._start_listener_thread')

        event = threading.Event()
        listener = ZmqListenerThread(self._receiver_socket_type, address,
                                     event, self)
        listener.start()

        # wait until the socket is bound in the listener
        for i in range(60):
            event.wait(1)
            if event.is_set():
                break

            if not listener.is_alive():
                break

        if not event.is_set():
            raise Exception('Listener thread could not be created')

        self._address = listener.get_address()

        return listener

    def forward_to_main(self, record):
        socket = self._get_socket()
        record_dict = record_to_dict(record, self)
        socket.send_json(record_dict)

    def _get_socket(self):
        pid = os.getpid()

        if self._pid != pid:
            # pid is None: new child forked from main
            # pid != os.getpid(): new child forked from other child
            self._client_bind_to_socket()
            self._pid = pid

        return self._socket

    def _client_bind_to_socket(self):
        socket = RobustZmqSocket(self._sender_socket_type, self._address)
        socket.connect()

        self._socket = socket

    def _close_socket(self):
        try:
            socket = self._socket
        except AttributeError:
            return
        else:
            if socket is not None:
                socket.close()
                self._socket = None

    def close(self):
        _log.info('ZmqHandler.close for %s', self)
        BaseMultiprocessHandler.close(self)

        try:
            if not self._is_main_process():
                return

            listener_thread = self._async_listener
            if listener_thread is None:
                return

            listener_thread.shutdown()
            listener_thread.join()
        finally:
            self._close_socket()


class ZmqListenerThread(threading.Thread):
    def __init__(self, socket_type, address, event, handler, *args, **kwargs):
        super(ZmqListenerThread, self).__init__(*args, **kwargs)
        self.setDaemon(True)

        self._event = event
        self._handler = handler
        self._running = True

        self._zmq_socket = RobustZmqSocket(
            socket_type, address, check=self._not_running)

    def _not_running(self):
        return not self._running

    def run(self):
        try:
            self._zmq_socket.bind()
            self._event.set()
            self._event = None

            while self._running:
                record_dict = self._zmq_socket.recv_json()
                if record_dict is None:
                    # receive timeout
                    continue

                self._process_record(record_dict)
        except RetryAbortedByCheck:
            # zmq bind failed and thread stopped running
            pass
        except Exception:
            _log.warning('exception in %s.run: %s',
                         self.__class__.__name__, traceback.format_exc())

        _log.info('%s stopped', self.__class__.__name__)
        self.close()

    def _process_record(self, record_dict):
        record = makeLogRecord(record_dict)
        self._handler.forward_to_sink(record)

    def get_address(self):
        return self._zmq_socket.address

    def close(self):
        """Close the zmq socket connection.
        """
        self._zmq_socket.close()

    def shutdown(self):
        """Gracful shutdown.
        """
        self._running = False
