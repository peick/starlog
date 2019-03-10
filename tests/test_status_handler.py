import logging
import warnings

import pytest

from starlog import StatusHandler
from starlog.status_handler import ReportLogRecord
from .records import all_records, plain_record


def test_init():
    handler = StatusHandler()
    assert handler
    handler.close()


def _check_report_log_record(record):
    dic = record.__dict__

    assert record.created > 0
    assert dic['created'] > 0
    assert dic['not_set_has_default'] == 0

    record.new_field = 123
    assert record.new_field == 123
    dic = record.__dict__
    assert dic['new_field'] == 123


@pytest.mark.parametrize('interval', [
    '0', '0s', '1', '1s', '5m', '1h',
    0, 1, 300, 3600,
])
def test_init_with_interval(interval, logged_records, status_sink_logger):
    # suppress 'interval is zero' warning
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')

        handler = StatusHandler(interval)
        handler.emit(plain_record)
        handler.close()

        # 0 second interval produces more than 1 status logs quickly
        assert len(logged_records) >= 1
        for record in logged_records:
            _check_report_log_record(record)


def test_init_with_negative_interval():
    with pytest.raises(ValueError):
        StatusHandler(-1)


def test_report_log_record():
    orig_record = logging.makeLogRecord({})
    record = ReportLogRecord(orig_record)

    _check_report_log_record(record)


@pytest.mark.parametrize('record', all_records)
def test_count_logs(record):
    handler = StatusHandler()
    handler.emit(record)
    handler.close()
