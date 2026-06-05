from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.alert import Alert
from src.models.alert_status import AlertStatus
from src.repositories.alert import AlertRepository
from src.schemas.alert import AlertCreate, AlertRead, AlertUpdate, PaginatedAlerts


class AlertService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        alert_repository: AlertRepository,
    ) -> None:
        self._session = session
        self._alerts = alert_repository

    async def create(self, *, organization_id: UUID, payload: AlertCreate) -> Alert:
        alert = await self._alerts.create(
            organization_id=organization_id,
            name=payload.name,
            metric_type=payload.metric_type,
            threshold=payload.threshold,
            window_minutes=payload.window_minutes,
        )
        await self._session.commit()
        return alert

    async def list(
        self,
        *,
        organization_id: UUID,
        limit: int,
        offset: int,
    ) -> PaginatedAlerts:
        items, total = await self._alerts.list_by_organization(
            organization_id=organization_id,
            limit=limit,
            offset=offset,
        )
        return PaginatedAlerts(
            items=[AlertRead.model_validate(a) for a in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get(self, *, alert_id: UUID, organization_id: UUID) -> Alert:
        alert = await self._alerts.get_by_id_and_org(
            alert_id=alert_id,
            organization_id=organization_id,
        )
        if alert is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found.",
            )
        return alert

    async def update(
        self,
        *,
        alert_id: UUID,
        organization_id: UUID,
        payload: AlertUpdate,
    ) -> Alert:
        alert = await self.get(alert_id=alert_id, organization_id=organization_id)
        update_data = payload.model_dump(exclude_unset=True)

        is_muted = update_data.pop("is_muted", None)
        for field, value in update_data.items():
            setattr(alert, field, value)

        if is_muted is True:
            alert.is_muted = True
            alert.status = AlertStatus.MUTED
        elif is_muted is False:
            alert.is_muted = False
            alert.status = AlertStatus.ACTIVE

        await self._session.commit()
        return alert

    async def delete(self, *, alert_id: UUID, organization_id: UUID) -> None:
        alert = await self.get(alert_id=alert_id, organization_id=organization_id)
        await self._alerts.delete(alert)
        await self._session.commit()
