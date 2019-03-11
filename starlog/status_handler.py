"""A log handler that examines every log and does some statistics on it.
It generates a log message in regular intervals.

Metrics that are collected:

- the number of messages per log level, available in formatter as:

  - ``%(DEBUG)d``
  - ``%(INFO)d``
  - ``%(WARN)d``
  - ``%(ERROR)d``
  - ``%(FATAL)d``

- the size of messages per log level, available in formatter as

  - ``%(DEBUG-SIZE)d``
  - ``%(INFO-SIZE)d``
  - ``%(WARN-SIZE)d``
  - ``%(ERROR-SIZE)d``
  - ``%(FATAL-SIZE)d``

- custom values examples::

    from starlog import inc
    logger.info('one more log line', extra=inc('requests').inc('2xx'))
    logger.info('bad request', extra=inc('4xx').update(error='Invalid input'))

  - ``%(requests)d``
  - ``%(2xx)d``
  - ``%(4xx)d``


Use case: write out status logs every some seconds to standard out and sent
full logs to syslog or a file.
"""
import logging
import logging.handlers
import re
import threading
import time
import traceback
import warnings
from collections import defaultdict

from .debug import get_debug_logger
from .log_entry import get_log_record_metric
from .metrics import MetricCollection


metric_collection = MetricCollection()

_log = get_debug_logger('starlog.debug.status_handler')


def _parse_interval(value):
    if not isinstance(value, int):
        match = re.match(r'(\d+)([smh]?)', value, flags=re.I)
        if not match:
            raise ValueError('interval is in wrong format: %r' % (value,))

        value = int(match.group(1))
        unit = match.group(2)

        if unit == 'm':
            value *= 60
        elif unit == 'h':
            value *= 3600

    if value < 0:
        raise ValueError('interval must be greater zero. Got: %r' % (value,))

    if value == 0:
        warnings.warn(
            'interval is zero. This could lead to high cpu consumption')

    return value


class StatusHandler(logging.Handler):
    """StatusHandler is a log handler that aggregates log messages and
    generates a status log message in regular intervals.

    :param str interval: the log status interval. Values must be of the format
        **Xs** (seconds), **Xm** (minutes) or **Xh** (hours), where **X** is
        a positive integer value. If you pass an integer instead of a string,
        then this value is taken as the number of seconds.
        Examples: **15s**, **5m**, **1h**
    :type interval: str or int

    Example::

        import logging
        import starlog
        import sys
        import time


        formatter = logging.Formatter('Seen info messages: %(INFO)d')
        handler = starlog.StatusHandler('1s')
        logging.root.addHandler(handler)
        logging.root.setLevel(logging.DEBUG)

        stdout = logging.StreamHandler(sys.stdout)
        stdout.setFormatter(formatter)
        logging.getLogger('starlog.status').addHandler(stdout)

        logging.root.info('you will not see this message - just the status')

        time.sleep(5)

        # output is:
        >>> Seen info messages: 1
        >>> Seen info messages: 0
        >>> Seen info messages: 0
        >>> Seen info messages: 0
        >>> Seen info messages: 0
    """
    def __init__(self, interval='5s', logger='starlog.status'):
        logging.Handler.__init__(self)
        self._metrics = metric_collection

        self._logger_name = logger
        self._async_reporter = self._start_reporter_thread(
            interval=interval,
            logger=logging.getLogger(logger))

    def emit(self, record):
        """Aggregates and collects metrics about the log record.
        The actual log record does not generate any direct output with this log
        handler. For this you must configure the logger ``starlog.status``
        """
        if record.name == self._logger_name:
            # if status logger was not configured with 'propagate=0'
            return
        self._count_messages(record)
        self._count_custom_metrics(record)

    def _count_messages(self, record):
        levelname = record.levelname or 'UNKNOWN'
        size = len(record.msg)
        self._metrics.inc(levelname)
        self._metrics.inc(levelname + '-SIZE', size)

    def _count_custom_metrics(self, record):
        metric = get_log_record_metric(record)
        if not metric:
            return

        for metric_key, value in metric.items():
            self._metrics.inc(metric_key, value)

    def _start_reporter_thread(self, **kwargs):
        _log.info('StatusHandler._start_reporter_thread')
        reporter_thread = ReporterThread(self._metrics, **kwargs)
        reporter_thread.start()
        return reporter_thread

    def close(self):
        _log.info('StatusHandler.close')
        logging.Handler.close(self)

        reporter_thread = self._async_reporter

        if reporter_thread is not None:
            reporter_thread.shutdown()
            reporter_thread.join()


class ReportLogRecord(object):
    def __init__(self, record):
        object.__setattr__(self, '_record', record)

    @property
    def __dict__(self):
        d = self._record.__dict__
        return defaultdict(lambda: 0, d)

    def __getattr__(self, key):
        return getattr(self._record, key)

    def __setattr__(self, key, value):
        setattr(self._record, key, value)


class ReporterThread(threading.Thread):
    def __init__(self, metrics, interval, logger, *args, **kwargs):
        super(ReporterThread, self).__init__(*args, **kwargs)
        self.setDaemon(True)

        self._metrics = metrics
        self._interval = _parse_interval(interval) * 2
        self._logger = logger
        self._running = True

    def shutdown(self):
        """Graceful shutdown.
        """
        _log.info('shutting down ReporterThread')
        self._running = False

    def run(self):
        try:
            while self._running:
                self._sleep()
                if self._running:
                    self._log_status()

            if self._metrics.has_metrics():
                self._log_status()
        except Exception:
            _log.warn('in ReporterThread.run: %s', traceback.format_exc())

    def _log_status(self):
        metrics = self._metrics.get_all_and_reset()

        record = logging.LogRecord(
            self._logger.name, logging.INFO, "", 0, "", (), None, None)
        record.__dict__.update(metrics)
        report_record = ReportLogRecord(record)

        self._logger.handle(report_record)

    def _sleep(self):
        for i in range(self._interval):
            if not self._running:
                break
            time.sleep(0.5)
