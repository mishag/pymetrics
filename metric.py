import time
import threading

from metric_aggregator import get_metric_aggregator


class Metric(object):
    def __init__(self, name):
        self._name = name
        self._start_time = None
        self._end_time = None
        self._aggregator = get_metric_aggregator()
        self._tid = threading.current_thread().ident

    def __enter__(self):
        self._start_time = time.time()
        self._aggregator.on_metric_enter(self)

    def __exit__(self, type, value, traceback):
        self._end_time = time.time()
        self._aggregator.on_metric_leave(self)

    @property
    def tid(self):
        return self._tid

    @property
    def total_time(self):
        return 1000 * (self._end_time - self._start_time)

    @property
    def name(self):
        return self._name

    def __str__(self):
        return "Metric: '{}' created: {}".format(self.name,
                                                 self._start_time)
