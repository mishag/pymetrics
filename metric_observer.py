from abc import ABCMeta, abstractmethod


class MetricObserver(metaclass=ABCMeta):

    @abstractmethod
    def notify(self, metric, stats):
        raise NotImplemented
