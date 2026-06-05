from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.alert_metric_type import AlertMetricType
from src.models.alert_status import AlertStatus


class AlertCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    metric_type: AlertMetricType
    threshold: float = Field(gt=0)
    window_minutes: int = Field(default=5, ge=1, le=1440)


class AlertUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    threshold: float | None = Field(default=None, gt=0)
    window_minutes: int | None = Field(default=None, ge=1, le=1440)
    is_muted: bool | None = None


class AlertHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    alert_id: UUID
    metric_value: float
    status: AlertStatus
    triggered_at: datetime


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    metric_type: AlertMetricType
    threshold: float
    window_minutes: int
    status: AlertStatus
    is_muted: bool
    created_at: datetime


class PaginatedAlerts(BaseModel):
    items: list[AlertRead]
    total: int
    limit: int
    offset: int
