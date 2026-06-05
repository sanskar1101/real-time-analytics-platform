from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.metric_type import MetricType
from src.models.widget import Widget
from src.models.widget_type import WidgetType


class WidgetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        dashboard_id: UUID,
        name: str,
        widget_type: WidgetType,
        metric_type: MetricType,
        time_range: str | None,
        position_x: int,
        position_y: int,
        width: int,
        height: int,
    ) -> Widget:
        widget = Widget(
            dashboard_id=dashboard_id,
            name=name,
            widget_type=widget_type,
            metric_type=metric_type,
            time_range=time_range,
            position_x=position_x,
            position_y=position_y,
            width=width,
            height=height,
        )
        self._session.add(widget)
        await self._session.flush()
        return widget

    async def get_by_id(self, widget_id: UUID) -> Widget | None:
        return await self._session.get(Widget, widget_id)

    async def list_by_dashboard(self, dashboard_id: UUID) -> list[Widget]:
        stmt = (
            select(Widget)
            .where(Widget.dashboard_id == dashboard_id)
            .order_by(Widget.created_at.asc())
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return list(rows)

    async def delete(self, widget: Widget) -> None:
        await self._session.delete(widget)
        await self._session.flush()
