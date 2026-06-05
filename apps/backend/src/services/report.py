from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.report import Report
from src.repositories.dashboard import DashboardRepository
from src.repositories.report import ReportRepository
from src.schemas.report import PaginatedReports, ReportCreate, ReportRead


class ReportService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        report_repository: ReportRepository,
        dashboard_repository: DashboardRepository,
    ) -> None:
        self._session = session
        self._reports = report_repository
        self._dashboards = dashboard_repository

    async def create(self, *, organization_id: UUID, payload: ReportCreate) -> Report:
        dashboard = await self._dashboards.get_by_id_and_org(
            dashboard_id=payload.dashboard_id,
            organization_id=organization_id,
        )
        if dashboard is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found.",
            )
        report = await self._reports.create(
            organization_id=organization_id,
            dashboard_id=payload.dashboard_id,
            name=payload.name,
            frequency=payload.frequency,
        )
        await self._session.commit()

        # Kick off initial generation immediately after creation.
        from src.tasks.reports import generate_report

        generate_report.delay(str(report.id))

        return report

    async def list(
        self,
        *,
        organization_id: UUID,
        limit: int,
        offset: int,
    ) -> PaginatedReports:
        items, total = await self._reports.list_by_organization(
            organization_id=organization_id,
            limit=limit,
            offset=offset,
        )
        return PaginatedReports(
            items=[ReportRead.model_validate(r) for r in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get(self, *, report_id: UUID, organization_id: UUID) -> Report:
        report = await self._reports.get_by_id_and_org(
            report_id=report_id,
            organization_id=organization_id,
        )
        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found.",
            )
        return report
