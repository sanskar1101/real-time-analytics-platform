from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.event import Event


class AnalyticsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_event_count(
        self,
        *,
        organization_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        stmt = (
            select(func.count()).select_from(Event).where(Event.organization_id == organization_id)
        )
        if start_date is not None:
            stmt = stmt.where(Event.event_timestamp >= start_date)
        if end_date is not None:
            stmt = stmt.where(Event.event_timestamp <= end_date)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_events_by_day(
        self,
        *,
        organization_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[tuple[date, int]]:
        day_col = func.date_trunc("day", Event.event_timestamp).label("day")
        stmt = select(day_col, func.count().label("count")).where(
            Event.organization_id == organization_id
        )
        if start_date is not None:
            stmt = stmt.where(Event.event_timestamp >= start_date)
        if end_date is not None:
            stmt = stmt.where(Event.event_timestamp <= end_date)
        stmt = stmt.group_by(day_col).order_by(day_col)
        rows = (await self._session.execute(stmt)).all()
        return [(row.day.date(), row.count) for row in rows]

    async def get_events_by_type(
        self,
        *,
        organization_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[tuple[str, int]]:
        stmt = select(Event.event_name, func.count().label("count")).where(
            Event.organization_id == organization_id
        )
        if start_date is not None:
            stmt = stmt.where(Event.event_timestamp >= start_date)
        if end_date is not None:
            stmt = stmt.where(Event.event_timestamp <= end_date)
        stmt = stmt.group_by(Event.event_name).order_by(func.count().desc())
        rows = (await self._session.execute(stmt)).all()
        return [(row.event_name, row.count) for row in rows]
