import errno
import threading

import flexmock
import pytest
import zmq

from starlog.handlers.zmq_handler import (
    BindFailedError, RobustZmqSocket, ZmqListenerThread)
from starlog import utils


address = 'tcp://127.0.0.1:34782'


@pytest.fixture(scope='function')
def dummy_zmq_handler():
    return flexmock()


@pytest.fixture(scope='function')
def listener():
    event = threading.Event()
    return ZmqListenerThread(zmq.PULL, address, event, dummy_zmq_handler)


@pytest.fixture(scope='function')
def receiver_socket():
    return RobustZmqSocket(zmq.PULL, address)


def test_robust_zmq_socket_bind_success_on_first_trial(receiver_socket):
    zmq_mock_socket = flexmock(closed=False, close=lambda: None)

    flexmock(zmq.Context).should_receive('socket') \
        .and_return(zmq_mock_socket)
    zmq_mock_socket.should_receive('bind').once()

    receiver_socket.bind()
    receiver_socket.close()


def test_robust_zmq_socket_bind_failed_unrecoverable(receiver_socket):
    zmq_mock_socket = flexmock(closed=True)

    flexmock(zmq.Context).should_receive('socket') \
        .and_return(zmq_mock_socket)
    zmq_mock_socket.should_receive('bind') \
        .and_raise(zmq.ZMQError(errno.EACCES)) \
        .once()

    with pytest.raises(BindFailedError):
        receiver_socket.bind()


def test_robust_zmq_socket_bind_failed_after_retries(receiver_socket):
    zmq_mock_socket = flexmock(closed=True)

    flexmock(zmq.Context).should_receive('socket') \
        .and_return(zmq_mock_socket)
    zmq_mock_socket.should_receive('bind') \
        .and_raise(zmq.ZMQError(errno.EBUSY))

    flexmock(utils).should_receive('sleep')

    with pytest.raises(zmq.ZMQError):
        receiver_socket.bind()


def test_robust_zmq_socket_bind_success_after_retries(receiver_socket):
    zmq_mock_socket = flexmock(closed=True)

    flexmock(zmq.Context).should_receive('socket') \
        .and_return(zmq_mock_socket)
    zmq_mock_socket.should_receive('bind') \
        .and_raise(zmq.ZMQError(errno.EBUSY)) \
        .and_return() \
        .times(2)

    flexmock(utils).should_receive('sleep')

    receiver_socket.bind()
    receiver_socket.close()
