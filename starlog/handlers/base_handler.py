import logging
import os
import warnings


class BaseMultiprocessHandler(logging.Handler):
    def __init__(self, logger):
        logging.Handler.__init__(self)

        self._parent_pid = os.getpid()
        self._sink_logger = logging.getLogger(logger)

    def emit(self, record):
        """If called by a subprocess, then the log record is send to the queue.

        If called by the main process, then the log record is forwarded to the
        the logger ``starlog.logsink`` or whatever was passed to the ``logger``
        parameter at instantiation of the MultiprocessHandler.
        """
        if self._is_main_process():
            self.forward_to_sink(record)
        else:
            self.forward_to_main(record)

    def _is_main_process(self):
        return self._parent_pid == os.getpid()

    def forward_to_sink(self, record):
        if not self._sink_logger.handlers:
            msg = 'The logger %s does not have any handlers configured' % (
                self._sink_logger.name)
            warnings.warn(msg, UserWarning)

        self._sink_logger.handle(record)

    def forward_to_main(self, record):
        raise NotImplementedError()
