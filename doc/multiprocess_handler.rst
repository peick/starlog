Multiprocess handler
====================

Defines several log handlers to operate in a multi-process application.

All log handler defined here are propagating log messages generated in a
sub-process to a central log process. From the central log process it's easier
to handle all log messages to a target log handler, like a file or syslog.

It depends on the way you created the sub-process to choose the right log handler.
Here's a short overview:

+------
| Sub-Process Created By |
+========================+
| os.fork()
| multiprocessing.Process()
| multiprocessing.Process() in "spawn" mode
+---------------------------------------------+

.. automodule:: starlog.multiprocess_handler
    :members:
