from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.report_frequency import ReportFrequency


class ReportCreate(BaseModel):
    dashboard_id: UUID
    name: str = Field(min_length=1, max_length=255)
    frequency: ReportFrequency


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    dashboard_id: UUID
    name: str
    frequency: ReportFrequency
    file_path: str | None
    last_generated_at: datetime | None
    created_at: datetime


class PaginatedReports(BaseModel):
    items: list[ReportRead]
    total: int
    limit: int
    offset: int
