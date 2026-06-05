from enum import Enum


class AlertMetricType(str, Enum):
    EVENT_COUNT = "EVENT_COUNT"
    ERROR_COUNT = "ERROR_COUNT"
