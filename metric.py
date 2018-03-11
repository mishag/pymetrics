import time
import threading
from functools import wraps

from metric_aggregator import get_metric_aggregator


_agg = get_metric_aggregator()


class Metric(object):
    def __init__(self, name, observable=True):
        self._name = name
        self._start_time = None
        self._end_time = None
        self._tid = threading.current_thread().ident
        self._observable = observable

    def __enter__(self):
        self._start_time = time.time()
        _agg._on_metric_enter(self)

    def __exit__(self, type, value, traceback):
        self._end_time = time.time()
        _agg._on_metric_leave(self)

    @property
    def tid(self):
        return self._tid

    @property
    def total_time(self):
        return 1000 * (self._end_time - self._start_time)

    @property
    def name(self):
        return self._name

    @property
    def observable(self):
        return self._observable

    def __str__(self):
        return "<Metric: '{}' created: {}>".format(self.name,
                                                   self._start_time)


def with_metric(name, observable=True):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            with Metric(name, observable):
                return func(*args, **kwargs)

        return wrapper

    return decorator
