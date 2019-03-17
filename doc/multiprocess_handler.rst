Multiprocess handler
====================

Defines several log handlers to operate in a multi-process application.

All log handler defined here are propagating log messages generated in a
sub-process to a central log process. From the central log process it's easier
to handle all log messages to a target log handler, like a file or syslog.

It depends on the way you created the sub-process to choose the right log handler.
Here's a short overview:

+----------------------------------------------------+------------------------------------------+
| Sub-Process Created By                             | Compatible Log Handler                   |
+====================================================+==========================================+
| os.fork()                                          | :py:class:`starlog.ZmqHandler`           |
+----------------------------------------------------+------------------------------------------+
| multiprocessing.Process()                          | :py:class:`starlog.MultiprocessHandler`, |
|                                                    | :py:class:`flexlog.ZmqHandler`           |
+----------------------------------------------------+------------------------------------------+
| multiprocessing.Process() in "spawn" mode          | :py:class:`starlog.ZmqHandler`           |
+----------------------------------------------------+------------------------------------------+

.. autoclass:: starlog.MultiprocessHandler
    :members:

.. autoclass:: starlog.ZmqHandler
    :members:
