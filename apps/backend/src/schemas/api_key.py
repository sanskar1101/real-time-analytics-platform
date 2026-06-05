from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class APIKeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class APIKeyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    is_active: bool
    created_at: datetime


class APIKeyCreated(APIKeyRead):
    key: str


class APIKeyRotated(BaseModel):
    id: UUID
    key: str
