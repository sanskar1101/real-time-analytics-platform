from enum import Enum


class AlertStatus(str, Enum):
    ACTIVE = "ACTIVE"
    TRIGGERED = "TRIGGERED"
    RESOLVED = "RESOLVED"
    MUTED = "MUTED"
