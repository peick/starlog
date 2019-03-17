import multiprocessing
import threading
import traceback

from .base_handler import BaseMultiprocessHandler
from .compat import QueueHandler
from .debug import get_debug_logger
from .utils import sleep


_log = get_debug_logger('starlog.debug.queue_handler')


class MultiprocessHandler(BaseMultiprocessHandler):
    """The MultiprocessHandler uses :py:class:`multiprocessing.Queue` to send
    log records between processes.

    All subprocesses sends messages to the queue in the `emit`
    method. A background thread of the main process retrieves these messages
    and delegates them to the ``logger`` (default: ``starlog.sink``) in the
    main process.

    The MultiprocessHandler is expected to be set up by the main process.

    :param queue: A multiprocessing capable queue. If not set, then a new
        multiprocessing queue is created.
    :param bool manager_queue: If `queue` is `None` and this argument is set
        to `True`, then a new queue is created by calling
        :py:meth:`multiprocessing.managers.SyncManager.Queue`.
    :param str logger: name of the logger where log records are send to in the
        main process.
    """

    def __init__(self, queue=None, manager_queue=True,
                 logger='starlog.logsink'):
        BaseMultiprocessHandler.__init__(self, logger)

        if queue is None:
            if manager_queue:
                manager = multiprocessing.Manager()
                queue = manager.Queue()
            else:
                queue = multiprocessing.Queue()
        else:
            self._check_queue(queue)

        self._queue = queue
        self._qhandler = QueueHandler(queue)

        self._async_listener = self._start_listener_thread(queue)

    def _check_queue(self, queue):
        """Check if ``queue`` has methods .get and .put
        """
        try:
            queue.get
            queue.put
        except AttributeError:
            raise TypeError('queue %r is of unsupported type: %s' % (
                queue, queue.__class__))

    def _start_listener_thread(self, queue):
        _log.info('MultiprocessHandler._start_listener_thread')
        listener = QueueListenerThread(queue, self)
        listener.start()
        return listener

    def forward_to_main(self, record):
        self._qhandler.handle(record)

    def close(self):
        _log.info('MultiprocessHandler.close for %s', self)
        BaseMultiprocessHandler.close(self)

        if not self._is_main_process():
            return

        self._shutdown_listener()

    def _shutdown_listener(self):
        listener_thread = self._async_listener
        if listener_thread is None:
            return

        queue = self._queue
        if queue is None:
            return

        # send signal to shutdown the QueueListenerThread
        try:
            queue.put(None)
        except (IOError, EOFError) as error:
            # probably the queue is already closed
            _log.warning('error while closing QueueListenerThread: %s', error)
            raise

        # wait until the thread consumed the shutdown item
        if not sleep(10, check=listener_thread.is_alive):
            _log.warning('QueueListenerThread did not shut down')

        _close_queue(queue)
        _join_queue(queue)
        self._queue = None
        self._async_listener = None


def _close_queue(queue):
    try:
        queue.close
    except AttributeError:
        pass
    else:
        _log.info('calling queue.close()')
        queue.close()
        _log.info('queue closed')


def _join_queue(queue):
    try:
        queue.join
    except AttributeError:
        pass
    else:
        _log.info('calling queue.join()')
        queue.join()
        _log.info('queue joined')


def _task_done(queue):
    try:
        queue.task_done
    except AttributeError:
        pass
    else:
        _log.info('QueueListenerThread: calling queue.task_done()')
        try:
            queue.task_done()
        except IOError:
            pass


class QueueListenerThread(threading.Thread):
    """Listens for incoming queue messages and forwards them back to the
    corresponding logger, i.e. in the main process.
    """
    def __init__(self, queue, handler, *args, **kwargs):
        super(QueueListenerThread, self).__init__(*args, **kwargs)
        self.setDaemon(True)

        self._queue = queue
        self._handler = handler

    def run(self):
        """Start the main loop. Wait for incoming log records in the queue.
        Each log record is forwarded back to python's standard logger of the
        main process.
        """
        try:
            while True:
                try:
                    # A closed queue results in an IOError in the get() request
                    # only if no timeout is set. A None value in the queue is
                    # a signal to stop the thread.
                    record = self._queue.get()
                    if record is None:
                        _log.info('shutting down QueueListenerThread')
                        break
                    self._process_record(record)
                except (IOError, EOFError):
                    # multiprocessing.managers.Queue returns an EOFError
                    _log.info('exception in QueueListenerThread.run: %s',
                              traceback.format_exc())
                    break
        except Exception:
            _log.warning('exception in QueueListenerThread.run: %s',
                         traceback.format_exc())

        _log.info('QueueListenerThread stopped')

        _task_done(self._queue)

    def _process_record(self, record):
        self._handler.forward_to_sink(record)
