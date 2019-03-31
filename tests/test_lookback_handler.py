import pytest
import six

from starlog import LookbackHandler
from .records import plain_record, plain_error_record, plain_old_record


@pytest.fixture(scope='function')
def handler(target_handler):
    return LookbackHandler(capacity=3, max_age=2, target=target_handler)


def buffered_records_count(handler):
    count = 0
    for key, records in six.iteritems(handler.buffer):
        count += len(records)

    return count


def test_emit(handler, logged_records):
    handler.emit(plain_record)
    assert len(logged_records) == 0
    assert buffered_records_count(handler) == 1

    handler.flush()
    assert len(logged_records) == 0
    assert buffered_records_count(handler) == 1


def test_emit_an_error(handler, logged_records):
    handler.emit(plain_error_record)
    assert len(logged_records) == 1
    assert buffered_records_count(handler) == 0

    handler.flush()
    assert len(logged_records) == 1
    assert buffered_records_count(handler) == 0


def test_emit_debug_and_error(handler, logged_records):
    handler.emit(plain_record)
    handler.emit(plain_error_record)
    assert len(logged_records) == 2
    assert buffered_records_count(handler) == 0

    handler.flush()
    assert len(logged_records) == 2
    assert buffered_records_count(handler) == 0


def test_drop_old_messages(handler, logged_records):
    handler.emit(plain_old_record)
    assert len(logged_records) == 0

    handler.flush()
    assert len(logged_records) == 0
    assert buffered_records_count(handler) == 0
