"""For debugging the starlog library.

To enable debugging you must set the environment variable ``STARLOG_DEBUG=1``
or via calling ``starlog.log_to_stderr()`` at the beginning of your code.
"""
import logging
import os
import sys


_logging_configured = False

STARLOG_DEBUG = os.environ.get('STARLOG_DEBUG', '0') == '1'


def get_debug_logger(logger_name):
    '''Returns the logger to debug starlog.
    '''
    assert logger_name.startswith('starlog.debug')

    _pre_configure_debug_logging()

    return logging.getLogger(logger_name)


def log_to_stderr(level=logging.DEBUG):
    global STARLOG_DEBUG, _logging_configured

    STARLOG_DEBUG = 1

    _logging_configured = False
    _pre_configure_debug_logging(level=level)


def _pre_configure_debug_logging(level=logging.DEBUG):
    """Do a pre configuration here at a very early stage even before
    logging.basicConfig or logging.fileConfig is called.
    """
    global _logging_configured

    if _logging_configured:
        return

    logger = logging.getLogger('starlog.debug')

    if not STARLOG_DEBUG:
        logger.disabled = True
        logger.setLevel(logging.CRITICAL)
    else:
        logger.info('starlog debug log activated')
        if not logger.handlers and logger.propagate:
            formatter = logging.Formatter('[%(name)s:%(process)d] %(message)s')
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.propagate = 0
            logger.setLevel(level)

    _logging_configured = True
