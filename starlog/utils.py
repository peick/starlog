import time


class RetryAbortedByCheck(Exception):
    pass


def sleep(duration, check=None, step=1.0):
    end = time.time() + duration
    rest = duration
    while rest > 0:
        if check is not None and check():
            return True

        if rest > step:
            time.sleep(step)
            rest = end - time.time()
        elif rest <= 0:
            return
        else:
            time.sleep(rest)
            return


def retry(exceptions=Exception, tries=3, backoff_factor=1, check=None,
          retry_log=None):
    """
    :param float backoff_factor: time sleep between retires is calculated with
        ``duration = backoff_factor * 2 ** (retries - 1)``
    :param callable check: A function / callable that is called on before every
        retry attempt. If value returned by ``check()`` evaluates to true,
        then ``retry`` raises a ``RetryAbortedByCheck`` exception.
    :param callable retry_log: A function / callable that is called before
        every retry attempt and on the last trial error. The function must
        accept the arguments ``retry_log(trial, last_trial=False)``
    """
    assert tries >= 0
    assert backoff_factor >= 0

    def wrap(fun):
        def deco(*args, **kwargs):
            last_trial = tries - 1
            for trial in range(tries):
                try:
                    return fun(*args, **kwargs)
                except exceptions:
                    is_last_trial = trial == last_trial

                    if retry_log is not None:
                        retry_log(trial, last_trial=is_last_trial)

                    if is_last_trial:
                        raise

                    duration = backoff_factor * 2 ** (tries - 1)

                    check_succeeds = sleep(duration, check)
                    if check_succeeds:
                        raise RetryAbortedByCheck()

        deco.__name__ = fun.__name__

        return deco

    return wrap
