import json
from logging import makeLogRecord, NullHandler
try:
    import cPickle as pickle
except ImportError:
    # python 3
    import pickle


null_handler = NullHandler()


def record_to_dict(record, handler=null_handler):
    # this function is the core of python's logging.handler.SocketHandler
    # method ``makePickle``

    ei = record.exc_info
    if ei:
        # just to get traceback text into record.exc_text ...
        handler.format(record)
    # See issue #14436: If msg or args are objects, they may not be
    # available on the receiving end. So we convert the msg % args
    # to a string, save it as msg and zap the args.
    d = dict(record.__dict__)
    d['msg'] = record.getMessage()
    d['args'] = None
    d['exc_info'] = None
    # Issue #25685: delete 'message' if present: redundant with 'msg'
    d.pop('message', None)
    return d


def pickle_log_record(record, handler=null_handler):
    """Pickles the record in binary format with a length prefix.
    """
    d = record_to_dict(record, handler=handler)
    s = pickle.dumps(d, 1)
    return s


def unpickle_log_record(data):
    """Creates a LogRecord from a pickled LogRecord.

    :param bytes data: pickled version of a LogRecord created by
        ``pickle_log_record``
    :return: a LogRecord
    """
    unpickled = pickle.loads(data)
    return makeLogRecord(unpickled)


def json_encode_log_record(record, handler=null_handler):
    d = record_to_dict(record, handler=null_handler)
    return json.dumps(d)


def json_decode_log_record(data):
    d = json.loads(data)
    return makeLogRecord(d)
