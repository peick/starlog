import pytest
import six
from logging import LogRecord

from starlog.serializer import (
    json_decode_log_record,
    json_encode_log_record,
    pickle_log_record,
    record_to_dict,
    unpickle_log_record)
from . import records


def _check_fluctuative_values(dic):
    created = dic.pop('created')
    msecs = dic.pop('msecs')
    process = dic.pop('process')
    relativeCreated = dic.pop('relativeCreated')
    thread = dic.pop('thread')
    dic.pop('stack_info', None)

    assert isinstance(created, float)
    assert isinstance(msecs, float)
    assert isinstance(process, int)
    assert isinstance(relativeCreated, float)
    assert isinstance(thread, int)


def test_record_to_dict():
    record = records.plain_record
    expectation = records.plain_record_dict

    dic = record_to_dict(record)

    _check_fluctuative_values(dic)
    assert dic == expectation


@pytest.mark.parametrize('record', records.all_records)
def test_pickle_log_record(record):
    pickled = pickle_log_record(record)

    assert pickled is not None
    assert isinstance(pickled, six.binary_type)


@pytest.mark.parametrize('record', records.all_records)
def test_unpickle_log_record(record):
    pickled = pickle_log_record(record)
    unpickled = unpickle_log_record(pickled)

    assert isinstance(unpickled, LogRecord)
    expectation = record_to_dict(record)

    assert unpickled.__dict__ == expectation


@pytest.mark.parametrize('record', records.all_records)
def test_json_encode_log_record(record):
    data = json_encode_log_record(record)
    assert isinstance(data, str), type(data)


@pytest.mark.parametrize('record', records.all_records)
def test_json_decode_log_record(record):
    data = json_encode_log_record(record)
    decoded = json_decode_log_record(data)

    assert isinstance(decoded, LogRecord)
    expectation = record_to_dict(record)

    assert decoded.__dict__ == expectation
