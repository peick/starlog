from __future__ import print_function
import logging
import logging.config
import os
import random
import multiprocessing
import time
from argparse import ArgumentParser

from starlog import inc


N = 5
T = 5


def _random_log_entry():
    loggername = random.choice(['example', 'example.app', None])
    logger = logging.getLogger(loggername)

    level = random.choice(['info', 'warning', 'error'])
    if level == 'info':
        logger.info('testing info logging',
                    extra=inc('requests').inc('foo').update({'OTHER': True}))
    if level == 'warning':
        logger.warning('testing warning logging')
    if level == 'error':
        logger.error('testing error logging')


def log_process():
    try:
        # logs for some seconds
        start = time.time()

        duration = 0
        while duration < T:
            _random_log_entry()
            time.sleep(random.random())
            duration = time.time() - start
        print("%s done" % (os.getpid(), ))
    except KeyboardInterrupt:
        pass


def main_loop_with_os_fork():
    print("starting main loop")

    pids = []

    for ti in range(N):
        pid = os.fork()
        if pid == 0:
            log_process()
            return

        pids.append(pid)

    _waitpids(pids)


def _waitpids(pids):
    for pid in pids:
        os.waitpid(pid, 0)


def main_loop_with_multiprocessing_process():
    print("starting main loop")

    px = []

    for ti in range(N):
        p = multiprocessing.Process(target=log_process)
        p.start()
        px.append(p)

    _join_processes(px)


def _join_processes(px):
    # if MultiprocessHandler parameter manager_queue is set to False,
    # then this is the pattern to join exited processes. The reason is,
    # multiprocessing.Queue sometimes blocks the process at p.join forever
    # although it left the run method.
    px[0].join(T + 1)

    for p in px:
        p.join(timeout=1)

    for p in px:
        if p.is_alive():
            print("terminating %s %s" % (p, p.pid))
            p.terminate()
            p.join()
    print("all processes exited")


def get_cli_args():
    parser = ArgumentParser()

    parser.add_argument(
        '--status',
        action='store_true',
        default=False,
        help='use starlog.StatusLogger')
    parser.add_argument(
        '--zmq',
        action='store_true',
        default=False,
        help='use starlog.ZmqHandler. If not set, then ' +
             'starlog.MultiprocessHandler is used. ')
    parser.add_argument(
        '--duration',
        type=int,
        default=5,
        help='How long the test should run in seconds')
    parser.add_argument(
        '--processes',
        type=int,
        default=5,
        help='The number of processes to start')
    parser.add_argument(
        '--fork',
        action='store_true',
        default=False,
        help='Use os.fork() to create a sub process. Default: use ' +
             'multiprocessing.Process')

    return parser.parse_args()


def main():
    global N, T

    args = get_cli_args()

    N = args.processes
    T = args.duration

    print("configuring logging")
    here = os.path.dirname(os.path.abspath(__file__))

    configs = {
        # status, zmq => log config file
        (False, False): 'logging_multiprocess.conf',
        (True,  False): 'logging_multiprocess_status.conf',
        (False,  True): 'logging_zmq.conf',
        (True,   True): 'logging_zmq_status.conf'}

    log_config_path = os.path.join(here, 'logging_zmq.conf')
    basename = configs[(args.status, args.zmq)]
    log_config_path = os.path.join(here, basename)
    logging.config.fileConfig(log_config_path, disable_existing_loggers=False)

    print("using %s" % basename)

    if args.fork:
        if not args.zmq:
            print('\nWARNING: the combination of os.fork and ' +
                  'starlog.MultiprocessHandler is not reliable and thus not ' +
                  'recommend\n')
        main_loop_with_os_fork()
    else:
        main_loop_with_multiprocessing_process()


if __name__ == '__main__':
    main()
