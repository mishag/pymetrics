from collections import defaultdict
import math
import sys


class MetricStats(object):
    def __init__(self):
        self.n = 0
        self.total_time = 0.0
        self.out_time = 0.0
        self.max_time = 0.0
        self.min_time = math.inf

    def __str__(self):
        return ("<n={n} total={total} outtime={outtime} "
                "maxtime={maxtime} mintime={}>".format(self.n,
                                                       self.total_time,
                                                       self.out_time,
                                                       self.max_time,
                                                       self.min_time))

    @property
    def avg_time(self):
        return self.total_time / self.n if self.n > 0 else 0.0

    @property
    def in_time(self):
        return self.total_time - self.out_time


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
        self._observers = []

    def register_observer(self, observer):
        self._observers.append(observer)

    def _notify_observers(self, metric, stats):
        if not metric.observable:
            return

        for observer in self._observers:
            observer.notify(metric, stats)

    def on_metric_enter(self, metric):
        thread_metric_stack = self._thread_metrics[metric.tid]
        thread_metric_stack.append(metric)

    def on_metric_leave(self, metric):
        stats = self._metric_map[metric.name]

        _update_metric_stats(stats, metric)

        self._notify_observers(metric, stats)

        thread_metric_stack = self._thread_metrics[metric.tid]

        assert len(thread_metric_stack) > 0

        thread_metric_stack.pop()

        if len(thread_metric_stack) > 0:
            prev_metric_stats = self._metric_map[thread_metric_stack[-1].name]
            prev_metric_stats.out_time += metric.total_time
        else:
            del self._thread_metrics[metric.tid]

    def print_metrics(self, fd=sys.stdout):

        width = (max(len(name) for name in self._metric_map)
                 if self._metric_map else 10)

        print("{metric:{width}} {n:>10} {total:>10} "
              "{out:>10} {inc:>10} {avg:>10} {max:>10} {min:>10}"
              .format(metric="Metric",
                      width=width,
                      n="n",
                      total="Total",
                      out="Outtime",
                      inc="Intime",
                      avg="Ave",
                      max="Max",
                      min="Min"),
              file=fd)

        for name, stats in self._metric_map.items():
            print("{name:{width}} {n:10} {total:10.4} "
                  "{out:10.4} {inc:>10.4} {avg:>10.4} {max:10.4} {min:10.4}"
                  .format(name=name,
                          width=width,
                          n=stats.n,
                          total=stats.total_time,
                          out=stats.out_time,
                          inc=stats.in_time,
                          avg=stats.avg_time,
                          max=stats.max_time,
                          min=stats.min_time),
                  file=fd)


__aggregator = None


def get_metric_aggregator():
    global __aggregator

    if __aggregator is None:
        __aggregator = MetricAggregator()

    return __aggregator
