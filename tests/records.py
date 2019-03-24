import logging

from starlog import inc


def makeLogRecord(dic, name='example.pkg', level=logging.DEBUG,
                  pathname="", lineno=0, msg="",
                  args=(), exc_info=None):
    record = logging.LogRecord(
        name, level, pathname, lineno, msg, args, exc_info)

    record.__dict__.update(dic)
    return record


plain_record = makeLogRecord({})

extra_field_record = makeLogRecord({'caller': 'joe'})

metric_record = makeLogRecord(inc('reqs'))

more_metrics_record = makeLogRecord(inc('reqs').inc('users', 5))

complex_record = makeLogRecord(
    inc('reqs').inc('users', 5).update({'caller': 'joe'}))

# record without fields:
# - created
# - msecs
# - process
# - relativeCreated
# - thread
# - stack_info [python 3 only]
plain_record_dict = {
    'args': None,
    'exc_info': None,
    'exc_text': None,
    'filename': '',
    'funcName': None,
    'levelname': 'DEBUG',
    'levelno': 10,
    'lineno': 0,
    'module': '',
    'msg': '',
    'name': 'example.pkg',
    'pathname': '',
    'processName': 'MainProcess',
    'threadName': 'MainThread'}


all_records = [
    complex_record,
    extra_field_record,
    metric_record,
    more_metrics_record,
    plain_record,
    ]


def make_thread_process_record(thread, process, level):
    return makeLogRecord({
        'levelno': level,
        'thread': thread,
        'process': process,
    })
