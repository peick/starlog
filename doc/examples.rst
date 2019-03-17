Examples
========

Status Handler
--------------

Execute with ``python doc/code/demo_status_handler.py --zmq``

code/demo_status_handler.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: code/demo_status_handler.py
   :language: python

code/logging.conf
~~~~~~~~~~~~~~~~~

.. literalinclude:: code/logging.conf
   :language: ini

ZMQ Handler
-----------

Execute with ``python doc/code/demo_multi_processing.py --zmq``

code/demo_multi_processing.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: code/demo_status_handler.py
   :language: python

code/logging_zmq.conf
~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: code/logging_zmq.conf
   :language: ini

gunicorn demo
-------------

code/gunicorn/app.py
~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: code/gunicorn/app.py
   :language: python

code/gunicorn/log.conf
~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: code/gunicorn/log.conf
   :language: ini

Output
~~~~~~

.. code:: bash

    $ gunicorn app:app --log-config log.conf
    2019-03-17 15:47:09,927 log messages: 0 CRITICAL, 0 ERROR, 0 WARNING 5 INFO, 0 DEBUG.
    2019-03-17 15:47:39,963 log messages: 0 CRITICAL, 0 ERROR, 0 WARNING 0 INFO, 0 DEBUG.
    2019-03-17 15:47:55,983 log messages: 0 CRITICAL, 0 ERROR, 0 WARNING 3 INFO, 0 DEBUG.

.. literalinclude:: code/gunicorn/demo.log
   :language: none
