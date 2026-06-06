from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.dashboard import Dashboard


class DashboardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        organization_id: UUID,
        name: str,
        description: str | None,
        is_public: bool,
    ) -> Dashboard:
        dashboard = Dashboard(
            organization_id=organization_id,
            name=name,
            description=description,
            is_public=is_public,
        )
        self._session.add(dashboard)
        await self._session.flush()
        return dashboard

    async def get_by_id(self, dashboard_id: UUID) -> Dashboard | None:
        return await self._session.get(Dashboard, dashboard_id)

    async def get_by_id_and_org(
        self,
        *,
        dashboard_id: UUID,
        organization_id: UUID,
    ) -> Dashboard | None:
        stmt = select(Dashboard).where(
            Dashboard.id == dashboard_id,
            Dashboard.organization_id == organization_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_organization(
        self,
        *,
        organization_id: UUID,
        limit: int,
        offset: int,
    ) -> tuple[list[Dashboard], int]:
        count_stmt = (
            select(func.count())
            .select_from(Dashboard)
            .where(Dashboard.organization_id == organization_id)
        )
        total: int = (await self._session.execute(count_stmt)).scalar_one()

        stmt = (
            select(Dashboard)
            .where(Dashboard.organization_id == organization_id)
            .order_by(Dashboard.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return list(rows), total

    async def get_public_with_widgets(self, dashboard_id: UUID) -> Dashboard | None:
        stmt = (
            select(Dashboard)
            .options(selectinload(Dashboard.widgets))
            .where(
                Dashboard.id == dashboard_id,
                Dashboard.is_public.is_(True),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, dashboard: Dashboard) -> None:
        await self._session.delete(dashboard)
        await self._session.flush()
