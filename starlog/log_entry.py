EXTRA_KEY = 'STARLOG_EXTRA'


class Extra(object):
    def __init__(self):
        self._dic = {}

    def update(self, dic):
        self._dic.update(dic)
        return self._dic

    def inc(self, metric_key, value=1):
        if EXTRA_KEY not in self._dic:
            self._dic[EXTRA_KEY] = {}

        self._dic[EXTRA_KEY][metric_key] = value
        return self

    def keys(self):
        return self._dic.keys()

    def values(self):
        return self._dic.values()

    def items(self):
        return self._dic.items()

    def iterkeys(self):
        return self._dic.iterkeys()

    def itervalues(self):
        return self._dic.itervalues()

    def iteritems(self):
        return self._dic.iteritems()

    def __getitem__(self, key):
        return self._dic[key]

    def __iter__(self):
        return iter(self._dic)


def inc(metric_key, value=1, dic=None):
    """For use in the `extra` parameter of logger.log() like

    logger.info('incoming request', extra=inc('requests'))

    logger.info('job done',
                extra=inc('jobs-done').inc('commits'))

    logger.info('some more meta data',
                extra=inc('changes').update({'caller': 'joe'}))
    """
    if dic is None:
        dic = Extra()

    dic.inc(metric_key, value)

    return dic


def get_log_record_metric(log_record):
    """Extract metric from log record.
    """
    return log_record.__dict__.get(EXTRA_KEY)
