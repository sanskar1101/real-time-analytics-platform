from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.analytics import AnalyticsRepository
from src.schemas.analytics import (
    EventCountResponse,
    EventsByDayItem,
    EventsByDayResponse,
    EventsByTypeItem,
    EventsByTypeResponse,
)


def _utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class AnalyticsService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        analytics_repository: AnalyticsRepository,
    ) -> None:
        self._session = session
        self._analytics = analytics_repository

    async def get_event_count(
        self,
        *,
        organization_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> EventCountResponse:
        total = await self._analytics.get_event_count(
            organization_id=organization_id,
            start_date=_utc(start_date),
            end_date=_utc(end_date),
        )
        return EventCountResponse(total=total)

    async def get_events_by_day(
        self,
        *,
        organization_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> EventsByDayResponse:
        rows = await self._analytics.get_events_by_day(
            organization_id=organization_id,
            start_date=_utc(start_date),
            end_date=_utc(end_date),
        )
        return EventsByDayResponse(
            items=[EventsByDayItem(date=d, count=c) for d, c in rows]
        )

    async def get_events_by_type(
        self,
        *,
        organization_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> EventsByTypeResponse:
        rows = await self._analytics.get_events_by_type(
            organization_id=organization_id,
            start_date=_utc(start_date),
            end_date=_utc(end_date),
        )
        return EventsByTypeResponse(
            items=[EventsByTypeItem(event_name=name, count=c) for name, c in rows]
        )
