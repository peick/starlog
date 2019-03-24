import logging

import pytest

from starlog import LookbackHandler
from ..records import make_thread_process_record


@pytest.fixture(scope='function')
def handler(target_handler):
    capacity = 5
    return LookbackHandler(capacity, target=target_handler)


def test_emit_buffer_overflow(handler, logged_records):
    thread_id = 1
    pid = 100

    for index in range(100):
        record = make_thread_process_record(thread_id, pid, logging.DEBUG)
        handler.emit(record)

        record = make_thread_process_record(thread_id, pid, logging.INFO)
        handler.emit(record)

        record = make_thread_process_record(thread_id, pid, logging.WARNING)
        handler.emit(record)

    assert len(logged_records) == 0


def test_emit_close(handler, logged_records):
    thread_id = 1
    pid = 100

    records = [
        make_thread_process_record(thread_id, pid, logging.DEBUG),
        make_thread_process_record(thread_id, pid, logging.INFO),
        make_thread_process_record(thread_id, pid, logging.WARNING)]

    for record in records:
        handler.emit(record)

    handler.close()
    assert len(logged_records) == 0


def test_emit_flush(handler, logged_records):
    thread_id = 1
    pid = 100

    records = [
        make_thread_process_record(thread_id, pid, logging.DEBUG),
        make_thread_process_record(thread_id, pid, logging.INFO),
        make_thread_process_record(thread_id, pid, logging.ERROR)]

    for record in records:
        handler.emit(record)

    assert logged_records == records
    del logged_records[:]

    handler.flush()
    assert len(logged_records) == 0


def test_emit_flush_multiple_threads(handler, logged_records):
    thread_id_1 = 1
    thread_id_2 = 2
    pid = 100

    t1_record_1 = make_thread_process_record(thread_id_1, pid, logging.DEBUG)
    t1_record_2 = make_thread_process_record(thread_id_1, pid, logging.WARNING)
    t1_record_3 = make_thread_process_record(thread_id_1, pid, logging.ERROR)

    t2_record_1 = make_thread_process_record(thread_id_2, pid, logging.DEBUG)
    t2_record_2 = make_thread_process_record(thread_id_2, pid, logging.WARNING)
    t2_record_3 = make_thread_process_record(thread_id_2, pid, logging.INFO)

    records = [
        t1_record_1,
        t2_record_1,
        t1_record_2,
        t2_record_2,
        t1_record_3,
        t2_record_3]

    for record in records:
        handler.emit(record)

    assert logged_records == [t1_record_1, t1_record_2, t1_record_3]


def test_emit_flush_multiple_processes(handler, logged_records):
    thread_id = 1
    pid_1 = 100
    pid_2 = 101

    p1_record_1 = make_thread_process_record(thread_id, pid_1, logging.DEBUG)
    p1_record_2 = make_thread_process_record(thread_id, pid_1, logging.WARNING)
    p1_record_3 = make_thread_process_record(thread_id, pid_1, logging.ERROR)

    p2_record_1 = make_thread_process_record(thread_id, pid_2, logging.DEBUG)
    p2_record_2 = make_thread_process_record(thread_id, pid_2, logging.WARNING)
    p2_record_3 = make_thread_process_record(thread_id, pid_2, logging.INFO)

    records = [
        p1_record_1,
        p2_record_1,
        p1_record_2,
        p2_record_2,
        p1_record_3,
        p2_record_3]

    for record in records:
        handler.emit(record)

    assert logged_records == [p1_record_1, p1_record_2, p1_record_3]
