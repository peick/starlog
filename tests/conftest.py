import logging

import pytest


class BufferingHandler(logging.Handler):
    def __init__(self, a_list):
        logging.Handler.__init__(self)
        self.buf = a_list

    def emit(self, record):
        self.buf.append(record)


@pytest.fixture(scope='function')
def logged_records():
    return list()


@pytest.fixture(scope='function')
def status_sink_logger(logged_records):
    # fyi: 'starlog.status' is the default logger for starlog.StatusHandler
    handler = BufferingHandler(logged_records)

    logger = logging.getLogger('starlog.status')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    return logger


@pytest.fixture(scope='function')
def sink_logger(logged_records):
    # fyi: 'starlog.logsink' is the default logger for
    # starlog.MultiprocessHandler
    handler = BufferingHandler(logged_records)

    logger = logging.getLogger('starlog.logsink')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    return logger
