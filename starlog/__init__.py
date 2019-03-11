from .debug import log_to_stderr
from .log_entry import inc
from .multiprocess_handler import MultiprocessHandler
from .status_handler import StatusHandler


def replace_callable_with_import_error(message):
    def wrap(*args, **kwargs):
        raise ImportError(message)
    return wrap


try:
    from .zmq_handler import ZmqPushPullHandler
except ImportError as error:
    message = '%s. Please install "starlog[zmq]"' % (error, )
    ZmqPushPullHandler = replace_callable_with_import_error(message)


__all__ = [
    'MultiprocessHandler',
    'StatusHandler',
    'ZmqPushPullHandler',
    'inc',
    'log_to_stderr',
    ]
