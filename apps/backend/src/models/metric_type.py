from enum import StrEnum


class MetricType(StrEnum):
    EVENT_COUNT = "EVENT_COUNT"
    EVENTS_BY_DAY = "EVENTS_BY_DAY"
    EVENTS_BY_TYPE = "EVENTS_BY_TYPE"
