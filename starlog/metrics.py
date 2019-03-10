import threading

import six


class CounterMetric(object):
    def __init__(self):
        self._value = 0
        self._count = 0

    def inc(self, value=1):
        self._value += value
        self._count += 1

    def value(self):
        return self._value

    def reset(self):
        self._value = 0
        self._count = 0

    def avg(self):
        if self._count == 0:
            return 0
        return float(self._value) / float(self._count)


class MetricCollection(object):
    def __init__(self):
        self._lock = threading.RLock()
        self._metrics = {}
        self._has_metrics = False

    def inc(self, metric_key, value=1):
        assert isinstance(metric_key, (six.binary_type, six.text_type))
        assert isinstance(value, int), value
        with self._lock:
            self._has_metrics = True
            metric = self._metrics.get(metric_key)
            if not metric:
                metric = CounterMetric()
                self._metrics[metric_key] = metric
            metric.inc(value)

    def has_metrics(self):
        return self._has_metrics

    def get_all_and_reset(self):
        retval = {}
        with self._lock:
            self._has_metrics = False
            for metric_key, metric in six.iteritems(self._metrics):
                retval[metric_key] = metric.value()
                retval[metric_key + '.avg'] = metric.avg()

                metric.reset()

        return retval
