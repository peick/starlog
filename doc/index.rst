Welcome to starlog's documentation!
===================================

starlog is a python library to improve python's standard logger capabilities.

Highlights:

- :doc:`status_handler`: log status lines in regular intervals
- :doc:`multiprocess_handler` bubble up messages of sub-processes to the main process when you need to deal with multiple processes

Installation of the latest stable version::

    pip install 'starlog[zmq]'

Installation of the latest pre-release / developer version::

    pip install --pre 'starlog[zmq]'

Installation of the latest pre-release / developer version from git::

    pip install 'git+https://gitlab.com/peick/starlog#egg=starlog[zmq]'

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   status_handler
   multiprocess_handler
   lookback_handler
   examples

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
