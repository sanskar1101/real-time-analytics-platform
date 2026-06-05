from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventCreate(BaseModel):
    event_name: str = Field(min_length=1, max_length=255)
    event_timestamp: datetime
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("event_name")
    @classmethod
    def normalize_event_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Event name cannot be empty.")
        return normalized

    @field_validator("event_timestamp")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Event timestamp must include timezone information.")
        return value.astimezone(timezone.utc)


class EventBatchCreate(BaseModel):
    events: list[EventCreate] = Field(min_length=1, max_length=1000)


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    source: str
    event_name: str
    event_timestamp: datetime
    payload: dict[str, Any]
    processed: bool
    created_at: datetime


class EventAccepted(BaseModel):
    id: UUID
    accepted: bool = True


class EventBatchAccepted(BaseModel):
    accepted_count: int
    event_ids: list[UUID]
