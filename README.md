# starlog

Python logging library to improve python's standard logger capabilities.

Features:

- Status log handler
- Multiprocess log handler

[Full Documentation](https://starlog.readthedocs.io/en/latest/)

## Examples

### Status Logger

A log handler that examines every log and does some statistics on it.
It generates a log message in regular intervals.

```
# minimalistic sample configuration for status logging
# The 'status' handler aggregates all log messages occurring at the 'root'
# logger. Every 5 seconds a status log line is sent by 'starlog.status' to
# its handler 'status_stdout'
[loggers]
keys = root, starlog.status

[handlers]
keys = status, status_stdout

[formatters]
keys = status

[logger_root]
level = NOTSET
handlers = status

[logger_starlog.status]
handlers = status_stdout
qualname = starlog.status

[handler_status]
class = starlog.StatusHandler
args = ()

[handler_status_stdout]
class = StreamHandler
args = (sys.stdout, )
formatter = status

[formatter_status]
format = %(asctime)s log messages: %(ERROR)d ERROR, %(WARNING)d WARNING %(INFO)d INFO
datefmt = %Y-%m-%d %H:%M:%S
```

Example usage:

```python
import logging

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

logging.info('Lorem ipsum dolor sit amet, consetetur sadipscing elitr, ')
logging.info('sed diam nonumy eirmod tempor invidunt ut labore et dolore ')
logging.info('magna aliquyam')
```

And the final output will look like:

```
2019-03-05 23:53:31 log messages: 0 ERROR, 0 WARNING 3 INFO
```
