import errno

import flexmock
import pytest
import zmq

from starlog.zmq_handler import (
    BindFailedError, RobustZmqSocket, ZmqListenerThread)
from starlog import utils


address = 'tcp://127.0.0.1:34782'


@pytest.fixture(scope='function')
def dummy_zmq_handler():
    return flexmock()


@pytest.fixture(scope='function')
def listener():
    return ZmqListenerThread(address, dummy_zmq_handler)


@pytest.fixture(scope='function')
def socket():
    return RobustZmqSocket(zmq.PULL, address)


def test_robust_zmq_socket_bind_success_on_first_trial(socket):
    zmq_mock_socket = flexmock(closed=False, close=lambda: None)

    flexmock(zmq.Context).should_receive('socket') \
        .and_return(zmq_mock_socket)
    zmq_mock_socket.should_receive('bind').once()

    socket.bind()
    socket.close()


def test_robust_zmq_socket_bind_failed_unrecoverable(socket):
    zmq_mock_socket = flexmock(closed=True)

    flexmock(zmq.Context).should_receive('socket') \
        .and_return(zmq_mock_socket)
    zmq_mock_socket.should_receive('bind') \
        .and_raise(zmq.ZMQError(errno.EACCES)) \
        .once()

    with pytest.raises(BindFailedError):
        socket.bind()


def test_robust_zmq_socket_bind_failed_after_retries(socket):
    zmq_mock_socket = flexmock(closed=True)

    flexmock(zmq.Context).should_receive('socket') \
        .and_return(zmq_mock_socket)
    zmq_mock_socket.should_receive('bind') \
        .and_raise(zmq.ZMQError(errno.EBUSY))

    flexmock(utils).should_receive('sleep')

    with pytest.raises(zmq.ZMQError):
        socket.bind()


def test_robust_zmq_socket_bind_success_after_retries(socket):
    zmq_mock_socket = flexmock(closed=True)

    flexmock(zmq.Context).should_receive('socket') \
        .and_return(zmq_mock_socket)
    zmq_mock_socket.should_receive('bind') \
        .and_raise(zmq.ZMQError(errno.EBUSY)) \
        .and_return() \
        .times(2)

    flexmock(utils).should_receive('sleep')

    socket.bind()
    socket.close()


# def test_zmq_listener_forward_log_message(listener, dummy_zmq_handler):
#     listener.start()
#     listener.shutdown()
#     listener.join()
