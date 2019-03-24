"""Outputs logs::

    2019-03-24 17:50:17 [   INFO] message 3
    2019-03-24 17:50:18 [   INFO] message 4
    2019-03-24 17:50:18 [   INFO] message 5
    2019-03-24 17:50:18 [  ERROR] message 6
    2019-03-24 17:50:24 [   INFO] message 16
    2019-03-24 17:50:24 [   INFO] message 17
    2019-03-24 17:50:25 [   INFO] message 18
    2019-03-24 17:50:25 [  ERROR] message 19
    2019-03-24 17:50:26 [   INFO] message 20
    2019-03-24 17:50:26 [WARNING] message 21
    2019-03-24 17:50:27 [WARNING] message 22
    2019-03-24 17:50:27 [  ERROR] message 23
"""
import logging
import logging.config
import os
import random
import time


_log = logging.getLogger(__name__)


def _random_log_entry(number):
    rand = random.random()
    if rand < 0.05:
        level = logging.ERROR
    elif rand < 0.2:
        level = logging.WARNING
    else:
        level = logging.INFO

    if level == logging.INFO:
        _log.info('message %d', number)
    if level == logging.WARNING:
        _log.warning('message %d', number)
    if level == logging.ERROR:
        _log.error('message %d', number)


def generate_logs():
    # logs for 30 seconds
    start = time.time()

    duration = 0
    number = 0
    while duration < 30:
        _random_log_entry(number)
        time.sleep(random.random())
        duration = time.time() - start
        number += 1


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    log_config_path = os.path.join(here, 'logging_lookback.conf')
    logging.config.fileConfig(log_config_path, disable_existing_loggers=False)

    generate_logs()


if __name__ == '__main__':
    main()
