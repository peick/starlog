import logging.handlers
import time
from collections import defaultdict

import six


class LookbackHandler(logging.handlers.MemoryHandler):
    """LookbackHandler is a handler which buffers logging records.

    Flushing occurs whenever an event of certain severity or greater is seen.

    When the buffer is full, logging records of lower severity levels are
    dropped.
    """
    def __init__(self, capacity, max_age=3600, **kwargs):
        logging.handlers.MemoryHandler.__init__(self, capacity, **kwargs)
        self.buffer = defaultdict(list)
        self.max_age = max_age

    def key(self, record):
        """Key of the record to identify the sub buffer. It returns
        a tuple of thread-id and process id of the record.
        """
        return (record.thread, record.process)

    def shouldFlush(self, record):
        """Check for record at the flushLevel or higher.
        """
        return record.levelno >= self.flushLevel

    def emit(self, record):
        """Emit a record.

        Append the record. If shouldFlush() tells us to, call
        flush_sub_buffer() to process the buffer.
        """
        self.trim()

        key = self.key(record)
        sub_buffer = self.buffer[key]
        sub_buffer.append(record)
        if self.shouldFlush(record):
            self.flush_sub_buffer(sub_buffer)

    def flush(self):
        """Flush all sub buffers.
        """
        self.trim()
        for records in six.itervalues(self.buffer):
            self.flush_sub_buffer(records)

    def flush_sub_buffer(self, records):
        """Sends buffered records of the thread/process record buffer to the
        target handler.
        """
        self.acquire()

        start = None
        end = None

        try:
            for index, record in enumerate(records):
                if record.levelno >= self.flushLevel:
                    end = index + 1

                    for rec in records[start:index + 1]:
                        self.target.handle(rec)

                    start = end

            if end is not None:
                del records[:end]
        finally:
            self.release()

    def trim(self):
        """Deletes buffered logging records reaching the buffer capacity.
        Also deletes logging records older than ``max_age``.
        """
        now = time.time()

        self.acquire()
        try:
            keys_to_delete = []

            for key, records in six.iteritems(self.buffer):
                del records[:-self.capacity]

                # drop old messages
                index = 0
                while index < len(records):
                    record = records[index]
                    if record.created and now - record.created > self.max_age:
                        del records[index]
                    else:
                        index += 1

                if len(records) == 0:
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                del self.buffer[key]

        finally:
            self.release()
