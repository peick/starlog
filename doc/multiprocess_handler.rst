Multiprocess handler
====================

Defines several log handlers to operate in a multi-process application.

All log handler defined here are propagating log messages generated in a
sub-process to a central log process. From the central log process it's easier
to handle all log messages to a target log handler, like a file or syslog.

It depends on the way you created the sub-process to choose the right log handler.
Here's a short overview:

+----------------------------------------------------+----------------------------------+
| Sub-Process Created By                             | Compatible Log Handler           |
+====================================================+==================================+
| os.fork()                                          | ``starlog.ZmqPushPullHandler``   |
+----------------------------------------------------+----------------------------------+
| multiprocessing.Process()                          | ``starlog.MultiprocessHandler``, |
|                                                    | ``flexlog.ZmqPushPullHandler``   |
+----------------------------------------------------+----------------------------------+
| multiprocessing.Process() in "spawn" mode          | ``starlog.ZmqPushPullHandler``   |
+----------------------------------------------------+----------------------------------+

.. autoclass:: starlog.MultiprocessHandler
    :members:

.. autoclass:: starlog.ZmqPushPullHandler
    :members:
