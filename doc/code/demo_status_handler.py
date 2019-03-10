"""Outputs status logs::

    2019-03-05 23:53:31 log messages: 1 ERROR, 4 WARNING 5 INFO
    2019-03-05 23:53:36 log messages: 4 ERROR, 4 WARNING 6 INFO
    2019-03-05 23:53:41 log messages: 6 ERROR, 1 WARNING 6 INFO
    2019-03-05 23:53:46 log messages: 2 ERROR, 3 WARNING 6 INFO
    2019-03-05 23:53:51 log messages: 3 ERROR, 2 WARNING 6 INFO
    2019-03-05 23:53:56 log messages: 0 ERROR, 3 WARNING 5 INFO
"""
import logging
import logging.config
import os
import random
import time


_log = logging.getLogger(__name__)


def _random_log_entry():
    level = random.choice(['info', 'warning', 'error'])
    if level == 'info':
        _log.info('testing info logging')
    if level == 'warning':
        _log.warn('testing warning logging')
    if level == 'error':
        _log.error('testing error logging')


def generate_logs():
    # logs for 30 seconds
    start = time.time()

    duration = 0
    while duration < 30:
        _random_log_entry()
        time.sleep(random.random())
        duration = time.time() - start


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    log_config_path = os.path.join(here, 'logging.conf')
    logging.config.fileConfig(log_config_path, disable_existing_loggers=False)

    generate_logs()


if __name__ == '__main__':
    main()
