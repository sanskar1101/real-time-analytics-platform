from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    title: str
    message: str
    is_read: bool
    created_at: datetime


class PaginatedNotifications(BaseModel):
    items: list[NotificationRead]
    total: int
    limit: int
    offset: int


class WebSocketNotification(BaseModel):
    type: str = "notification"
    id: str
    title: str
    message: str
    created_at: str
