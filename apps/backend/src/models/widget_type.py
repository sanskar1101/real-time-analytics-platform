from enum import Enum


class WidgetType(str, Enum):
    KPI = "KPI"
    LINE = "LINE"
    BAR = "BAR"
    PIE = "PIE"
