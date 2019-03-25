import logging

import pytest

from starlog import inc


@pytest.fixture(scope='function')
def logger():
    inst = logging.getLogger(__name__)
    inst.setLevel(logging.DEBUG)
    return inst


def test_inc_in_logging(logger):
    logger.info('test', extra=inc('reqs'))


def test_inc_update_in_logging(logger):
    logger.info('test', extra=inc('reqs').update({'more': 'content'}))


def test_inc_make_log_record():
    logging.makeLogRecord(inc('reqs'))
