from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Event


class EventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        organization_id: UUID,
        source: str,
        event_name: str,
        event_timestamp: datetime,
        payload: dict[str, Any],
    ) -> Event:
        event = Event(
            organization_id=organization_id,
            source=source,
            event_name=event_name,
            event_timestamp=event_timestamp,
            payload=payload,
        )
        self._session.add(event)
        await self._session.flush()
        return event

    async def create_many(
        self,
        *,
        organization_id: UUID,
        source: str,
        events: list[tuple[str, datetime, dict[str, Any]]],
    ) -> list[Event]:
        event_models = [
            Event(
                organization_id=organization_id,
                source=source,
                event_name=event_name,
                event_timestamp=event_timestamp,
                payload=payload,
            )
            for event_name, event_timestamp, payload in events
        ]
        self._session.add_all(event_models)
        await self._session.flush()
        return event_models

    async def get_by_id(self, event_id: UUID) -> Event | None:
        return await self._session.get(Event, event_id)
