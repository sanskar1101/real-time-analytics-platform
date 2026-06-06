from enum import StrEnum


class AlertStatus(StrEnum):
    ACTIVE = "ACTIVE"
    TRIGGERED = "TRIGGERED"
    RESOLVED = "RESOLVED"
    MUTED = "MUTED"
