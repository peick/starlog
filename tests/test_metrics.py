from starlog.metrics import CounterMetric, MetricCollection


def test_counter_metric_inc():
    cnt = CounterMetric()

    cnt.inc()
    assert cnt.value() == 1

    cnt.inc()
    assert cnt.value() == 2


def test_counter_metric_avg():
    cnt = CounterMetric()

    assert cnt.avg() == 0.0

    cnt.inc()
    assert cnt.avg() == 1.0

    cnt.inc(11)
    assert cnt.avg() == 6.0


def test_counter_metric_reset():
    cnt = CounterMetric()

    assert cnt.value() == 0

    cnt.inc()
    assert cnt.value() == 1

    cnt.reset()
    assert cnt.value() == 0


def test_metric_collection_empty_get_all():
    coll = MetricCollection()

    result = coll.get_all_and_reset()
    assert result == {}


def test_metric_collection_inc_single_counter():
    coll = MetricCollection()

    coll.inc('reqs')

    result = coll.get_all_and_reset()
    assert result == {'reqs': 1, 'reqs.avg': 1.0}

    result = coll.get_all_and_reset()
    assert result == {'reqs': 0, 'reqs.avg': 0}


def test_metric_collection_inc_multiple_counter():
    coll = MetricCollection()

    coll.inc('reqs')
    coll.inc('users', 4)
    coll.inc('users', 8)

    result = coll.get_all_and_reset()
    assert result == {'reqs': 1, 'reqs.avg': 1.0,
                      'users': 12, 'users.avg': 6.0}

    result = coll.get_all_and_reset()
    assert result == {'reqs': 0, 'reqs.avg': 0,
                      'users': 0, 'users.avg': 0}

