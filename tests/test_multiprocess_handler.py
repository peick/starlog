import logging
import logging.handlers
import warnings
from multiprocessing import Process, Queue

import flexmock
import pytest

from starlog.multiprocess_handler import QueueListenerThread
from starlog import MultiprocessHandler
from .records import plain_record


@pytest.fixture(scope='function')
def queue():
    return Queue()


@pytest.fixture(scope='function')
def dummy_mp_handler():
    return flexmock()


@pytest.fixture(scope='function')
def listener(queue, dummy_mp_handler):
    return QueueListenerThread(queue, dummy_mp_handler)


def test_queue_listener_with_a_closed_queue(queue, listener):
    queue.close()
    listener.run()


def test_queue_listener_forward_log_message(queue, listener, dummy_mp_handler):
    dummy_mp_handler \
        .should_receive('forward_to_sink') \
        .once()

    listener.start()
    queue.put(plain_record)
    queue.put(None)
    listener.join()


def test_multiprocess_handler_forward_to_sink(queue, sink_logger,
                                              logged_records):
    mph = MultiprocessHandler(queue)

    mph.emit(plain_record)

    # cleanup
    mph.close()

    assert len(logged_records) == 1


def test_multiprocess_handler_warn_no_handlers(queue):
    # suppress warning:
    #   'The logger starlog.logsink does not have any handlers configured'
    mph = MultiprocessHandler(queue)

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')

        mph.emit(plain_record)

        # cleanup
        mph.close()


def test_multiprocess_handler_with_a_subprocess(queue, sink_logger,
                                                logged_records):
    def emitter():
        logging.getLogger('example.pkg').info('sample message')

    mph = MultiprocessHandler(queue)

    logger = logging.getLogger('example')
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(mph)

    process = Process(target=emitter)
    process.start()
    process.join()

    # cleanup
    mph.close()

    assert len(logged_records) == 1
