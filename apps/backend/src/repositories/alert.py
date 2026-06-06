from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.alert import Alert
from src.models.alert_history import AlertHistory
from src.models.alert_metric_type import AlertMetricType
from src.models.alert_status import AlertStatus


class AlertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        organization_id: UUID,
        name: str,
        metric_type: AlertMetricType,
        threshold: float,
        window_minutes: int,
    ) -> Alert:
        alert = Alert(
            organization_id=organization_id,
            name=name,
            metric_type=metric_type,
            threshold=threshold,
            window_minutes=window_minutes,
            status=AlertStatus.ACTIVE,
            is_muted=False,
        )
        self._session.add(alert)
        await self._session.flush()
        return alert

    async def get_by_id_and_org(
        self,
        *,
        alert_id: UUID,
        organization_id: UUID,
    ) -> Alert | None:
        stmt = select(Alert).where(
            Alert.id == alert_id,
            Alert.organization_id == organization_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_organization(
        self,
        *,
        organization_id: UUID,
        limit: int,
        offset: int,
    ) -> tuple[list[Alert], int]:
        count_stmt = (
            select(func.count()).select_from(Alert).where(Alert.organization_id == organization_id)
        )
        total: int = (await self._session.execute(count_stmt)).scalar_one()

        stmt = (
            select(Alert)
            .where(Alert.organization_id == organization_id)
            .order_by(Alert.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return list(rows), total

    async def list_evaluatable(self) -> list[Alert]:
        """Return all non-muted alerts that require ongoing evaluation."""
        stmt = select(Alert).where(
            Alert.is_muted.is_(False),
            Alert.status.in_([AlertStatus.ACTIVE, AlertStatus.TRIGGERED, AlertStatus.RESOLVED]),
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return list(rows)

    async def create_history(
        self,
        *,
        alert_id: UUID,
        metric_value: float,
        status: AlertStatus,
    ) -> AlertHistory:
        entry = AlertHistory(
            alert_id=alert_id,
            metric_value=metric_value,
            status=status,
        )
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def delete(self, alert: Alert) -> None:
        await self._session.delete(alert)
        await self._session.flush()
