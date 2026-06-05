from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.metric_type import MetricType
from src.models.widget_type import WidgetType


class WidgetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    widget_type: WidgetType
    metric_type: MetricType
    time_range: str | None = Field(default=None, max_length=50)
    position_x: int = Field(default=0, ge=0)
    position_y: int = Field(default=0, ge=0)
    width: int = Field(default=4, ge=1)
    height: int = Field(default=3, ge=1)


class WidgetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    widget_type: WidgetType | None = None
    metric_type: MetricType | None = None
    time_range: str | None = Field(default=None, max_length=50)
    position_x: int | None = Field(default=None, ge=0)
    position_y: int | None = Field(default=None, ge=0)
    width: int | None = Field(default=None, ge=1)
    height: int | None = Field(default=None, ge=1)


class WidgetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    dashboard_id: UUID
    name: str
    widget_type: WidgetType
    metric_type: MetricType
    time_range: str | None
    position_x: int
    position_y: int
    width: int
    height: int
    created_at: datetime
