from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.dashboard import Dashboard
from src.models.widget import Widget
from src.repositories.dashboard import DashboardRepository
from src.repositories.widget import WidgetRepository
from src.schemas.dashboard import DashboardCreate, DashboardRead, DashboardUpdate, PaginatedDashboards
from src.schemas.widget import WidgetCreate, WidgetUpdate


class DashboardService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        dashboard_repository: DashboardRepository,
    ) -> None:
        self._session = session
        self._dashboards = dashboard_repository

    async def create(self, *, organization_id: UUID, payload: DashboardCreate) -> Dashboard:
        dashboard = await self._dashboards.create(
            organization_id=organization_id,
            name=payload.name,
            description=payload.description,
            is_public=payload.is_public,
        )
        await self._session.commit()
        return dashboard

    async def list(
        self,
        *,
        organization_id: UUID,
        limit: int,
        offset: int,
    ) -> PaginatedDashboards:
        items, total = await self._dashboards.list_by_organization(
            organization_id=organization_id,
            limit=limit,
            offset=offset,
        )
        return PaginatedDashboards(
            items=[DashboardRead.model_validate(d) for d in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get(self, *, dashboard_id: UUID, organization_id: UUID) -> Dashboard:
        dashboard = await self._dashboards.get_by_id_and_org(
            dashboard_id=dashboard_id,
            organization_id=organization_id,
        )
        if dashboard is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found.",
            )
        return dashboard

    async def update(
        self,
        *,
        dashboard_id: UUID,
        organization_id: UUID,
        payload: DashboardUpdate,
    ) -> Dashboard:
        dashboard = await self.get(
            dashboard_id=dashboard_id, organization_id=organization_id
        )
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(dashboard, field, value)
        await self._session.commit()
        return dashboard

    async def delete(self, *, dashboard_id: UUID, organization_id: UUID) -> None:
        dashboard = await self.get(
            dashboard_id=dashboard_id, organization_id=organization_id
        )
        await self._dashboards.delete(dashboard)
        await self._session.commit()


class WidgetService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        dashboard_repository: DashboardRepository,
        widget_repository: WidgetRepository,
    ) -> None:
        self._session = session
        self._dashboards = dashboard_repository
        self._widgets = widget_repository

    async def _require_dashboard(
        self, *, dashboard_id: UUID, organization_id: UUID
    ) -> Dashboard:
        dashboard = await self._dashboards.get_by_id_and_org(
            dashboard_id=dashboard_id,
            organization_id=organization_id,
        )
        if dashboard is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found.",
            )
        return dashboard

    async def _require_widget_in_org(
        self, *, widget_id: UUID, organization_id: UUID
    ) -> Widget:
        widget = await self._widgets.get_by_id(widget_id)
        if widget is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found.",
            )
        await self._require_dashboard(
            dashboard_id=widget.dashboard_id,
            organization_id=organization_id,
        )
        return widget

    async def create(
        self,
        *,
        dashboard_id: UUID,
        organization_id: UUID,
        payload: WidgetCreate,
    ) -> Widget:
        await self._require_dashboard(
            dashboard_id=dashboard_id, organization_id=organization_id
        )
        widget = await self._widgets.create(
            dashboard_id=dashboard_id,
            name=payload.name,
            widget_type=payload.widget_type,
            metric_type=payload.metric_type,
            time_range=payload.time_range,
            position_x=payload.position_x,
            position_y=payload.position_y,
            width=payload.width,
            height=payload.height,
        )
        await self._session.commit()
        return widget

    async def list(self, *, dashboard_id: UUID, organization_id: UUID) -> list[Widget]:
        await self._require_dashboard(
            dashboard_id=dashboard_id, organization_id=organization_id
        )
        return await self._widgets.list_by_dashboard(dashboard_id)

    async def update(
        self,
        *,
        widget_id: UUID,
        organization_id: UUID,
        payload: WidgetUpdate,
    ) -> Widget:
        widget = await self._require_widget_in_org(
            widget_id=widget_id, organization_id=organization_id
        )
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(widget, field, value)
        await self._session.commit()
        return widget

    async def delete(self, *, widget_id: UUID, organization_id: UUID) -> None:
        widget = await self._require_widget_in_org(
            widget_id=widget_id, organization_id=organization_id
        )
        await self._widgets.delete(widget)
        await self._session.commit()
