from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.report import Report
from src.models.report_frequency import ReportFrequency


class ReportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        organization_id: UUID,
        dashboard_id: UUID,
        name: str,
        frequency: ReportFrequency,
    ) -> Report:
        report = Report(
            organization_id=organization_id,
            dashboard_id=dashboard_id,
            name=name,
            frequency=frequency,
        )
        self._session.add(report)
        await self._session.flush()
        return report

    async def get_by_id(self, report_id: UUID) -> Report | None:
        return await self._session.get(Report, report_id)

    async def get_by_id_and_org(
        self,
        *,
        report_id: UUID,
        organization_id: UUID,
    ) -> Report | None:
        stmt = select(Report).where(
            Report.id == report_id,
            Report.organization_id == organization_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_organization(
        self,
        *,
        organization_id: UUID,
        limit: int,
        offset: int,
    ) -> tuple[list[Report], int]:
        count_stmt = (
            select(func.count())
            .select_from(Report)
            .where(Report.organization_id == organization_id)
        )
        total: int = (await self._session.execute(count_stmt)).scalar_one()

        stmt = (
            select(Report)
            .where(Report.organization_id == organization_id)
            .order_by(Report.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return list(rows), total

    async def list_by_frequency(self, frequency: ReportFrequency) -> list[Report]:
        stmt = select(Report).where(Report.frequency == frequency)
        rows = (await self._session.execute(stmt)).scalars().all()
        return list(rows)

    async def update_generation_result(
        self,
        *,
        report_id: UUID,
        file_path: str,
        last_generated_at: datetime,
    ) -> None:
        report = await self.get_by_id(report_id)
        if report is not None:
            report.file_path = file_path
            report.last_generated_at = last_generated_at
            await self._session.flush()
