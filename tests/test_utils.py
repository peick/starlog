import time

import flexmock
import pytest

from starlog.utils import retry, sleep, RetryAbortedByCheck


def test_sleep_zero():
    flexmock(time).should_receive('sleep').never()
    sleep(0)


def test_sleep_some_seconds():
    flexmock(time).should_receive('sleep').times(3)
    flexmock(time).should_receive('time') \
        .and_return(18.3) \
        .and_return(19.3) \
        .and_return(20.3)

    sleep(2.5)


def test_sleep_check():
    status = [True, False]

    def check():
        return status.pop()

    flexmock(time).should_receive('sleep').times(1)
    flexmock(time).should_receive('time') \
        .and_return(18.3) \
        .and_return(19.3)

    sleep(2.5, check=check)


def test_retry_success():
    @retry()
    def works_without_problems():
        return 42

    response = works_without_problems()
    assert response == 42


def test_retry_success_after_retries():
    should_raise = [True, False]

    @retry()
    def works_on_second_trial():
        if should_raise.pop():
            raise Exception('Something bad happenend')
        return 42

    response = works_on_second_trial()
    assert response == 42


def test_retry_with_custom_exceptions():
    should_raise = [True, False]

    @retry(ValueError)
    def raises_type_error():
        if should_raise.pop():
            raise ValueError()
        raise TypeError()

    with pytest.raises(TypeError):
        raises_type_error()


def test_retry_failed():
    @retry(backoff_factor=0.01)
    def always_raises():
        raise ValueError()

    with pytest.raises(ValueError):
        always_raises()


def test_retry_with_check():
    status = [True, False]

    def good_on_second_request():
        return status.pop()

    @retry(check=good_on_second_request, backoff_factor=0.01)
    def always_raises():
        raise ValueError()

    with pytest.raises(RetryAbortedByCheck):
        always_raises()
