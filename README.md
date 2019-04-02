# starlog

A python library to improve python's standard logger capabilities.

Available logging handlers:

- Status log handler - aggregates log records
- Multiprocess log handler (`multiprocessing.Queue` or `zmq` based)
- Lookback log handler - logs more verbose older log records in case an error is logged

[Full Documentation](https://starlog.readthedocs.io/en/latest/)


## Status Log Handler

A log handler that aggregates every log and does some statistics on it.
It generates a log message in regular intervals.


Example usage:

```python
import logging

logging.config.fileConfig('logging-status.conf', disable_existing_loggers=False)

logging.info('Lorem ipsum dolor sit amet, consetetur sadipscing elitr, ')
logging.info('sed diam nonumy eirmod tempor invidunt ut labore et dolore ')
logging.info('magna aliquyam')
```

The final output prints 1 log line.

```
2019-03-05 23:53:31 log messages: 0 ERROR, 0 WARNING 3 INFO
```


## Lookback Log Handler

```python
import logging

# with capacity=2
logging.config.fileConfig('logging-lookback.conf', disable_existing_loggers=False)

logging.info('Lorem ipsum ')
logging.info('dolor sit amet, ')
logging.info('consetetur sadipscing elitr, ')
logging.info('sed diam nonumy eirmod ')
logging.info('tempor invidunt ut labore et dolore ')
logging.error('magna aliquyam')
```

The final output will only print the last 3 logs.

```
2019-03-24 17:50:18 [   INFO] sed diam nonumy eirmod
2019-03-24 17:50:18 [   INFO] tempor invidunt ut labore et dolore
2019-03-24 17:50:25 [  ERROR] magna aliquyam
```
