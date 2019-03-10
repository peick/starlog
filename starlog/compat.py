
try:
    from logging.handlers import QueueHandler
except ImportError:
    # python < 3.2
    #
    # The class QueueHandler is a direct copy of the implementation of the
    # one from the standard python library.

    import logging

    class QueueHandler(logging.Handler):
        def __init__(self, queue):
            logging.Handler.__init__(self)
            self.queue = queue

        def enqueue(self, record):
            self.queue.put_nowait(record)

        def prepare(self, record):
            self.format(record)
            record.msg = record.message
            record.args = None
            record.exc_info = None
            return record

        def emit(self, record):
            try:
                self.enqueue(self.prepare(record))
            except Exception:
                self.handleError(record)


__all__ = ['QueueHandler']
