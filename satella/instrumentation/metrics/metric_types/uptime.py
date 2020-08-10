import time
import typing as tp

from .base import LeafMetric
from .registry import register_metric
from ..data import MetricDataCollection, MetricData


@register_metric
class UptimeMetric(LeafMetric):
    """
    A metric that gives the difference between current value of time_getter
    and it's value at the initialization of this metric
    """
    __slots__ = ('time_getter', 'basic_time')

    CLASS_NAME = 'uptime'
    CONSTRUCTOR = str

    def __init__(self, *args, time_getter: tp.Callable[[], float] = time.monotonic,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.time_getter = time_getter
        self.basic_time = time_getter()

    def _handle(self, *args, **kwargs) -> None:
        raise TypeError('You are not supposed to call this!')

    def to_metric_data(self) -> tp.Union[list, dict, str, int, float, None]:
        if self.embedded_submetrics_enabled:
            return super().to_metric_data()
        return MetricDataCollection(
            MetricData(self.name,
                       self.time_getter() - self.basic_time,
            self.labels, self.get_timestamp(), self.internal)
        )