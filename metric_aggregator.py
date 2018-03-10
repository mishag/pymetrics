from collections import defaultdict
import math


class MetricStats(object):
    def __init__(self):
        self.n = 0
        self.total_time = 0
        self.out_time = 0
        self.max_time = 0
        self.min_time = math.inf


__aggregator = None


def _update_metric_stats(stats, metric):
    stats.n += 1
    stats.total_time += metric.total_time

    if stats.max_time < metric.total_time:
        stats.max_time = metric.total_time

    if stats.min_time > metric.total_time:
        stats.min_time = metric.total_time


class MetricAggregator(object):
    def __init__(self):
        self._thread_metrics = defaultdict(list)
        self._metric_map = defaultdict(MetricStats)

    def on_metric_enter(self, metric):
        thread_metric_stack = self._thread_metrics[metric.tid]
        thread_metric_stack.append(metric)

    def on_metric_leave(self, metric):
        stats = self._metric_map[metric.name]

        _update_metric_stats(stats, metric)

        thread_metric_stack = self._thread_metrics[metric.tid]

        assert len(thread_metric_stack) > 0

        thread_metric_stack.pop()

        if len(thread_metric_stack) > 0:
            prev_metric_stats = self._metric_map[thread_metric_stack[-1].name]
            prev_metric_stats.out_time += stats.total_time
        else:
            del self._thread_metrics[metric.tid]


def get_metric_aggregator():
    global __aggregator

    if __aggregator is None:
        __aggregator = MetricAggregator()

    return __aggregator
