from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import TenantContext, get_alert_service, get_tenant_context
from src.schemas.alert import AlertCreate, AlertRead, AlertUpdate, PaginatedAlerts
from src.services.alert import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post("", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
async def create_alert(
    payload: AlertCreate,
    ctx: TenantContext = Depends(get_tenant_context),
    service: AlertService = Depends(get_alert_service),
) -> AlertRead:
    alert = await service.create(organization_id=ctx.organization_id, payload=payload)
    return AlertRead.model_validate(alert)


@router.get("", response_model=PaginatedAlerts)
async def list_alerts(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    ctx: TenantContext = Depends(get_tenant_context),
    service: AlertService = Depends(get_alert_service),
) -> PaginatedAlerts:
    return await service.list(
        organization_id=ctx.organization_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{alert_id}", response_model=AlertRead)
async def get_alert(
    alert_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    service: AlertService = Depends(get_alert_service),
) -> AlertRead:
    alert = await service.get(alert_id=alert_id, organization_id=ctx.organization_id)
    return AlertRead.model_validate(alert)


@router.patch("/{alert_id}", response_model=AlertRead)
async def update_alert(
    alert_id: UUID,
    payload: AlertUpdate,
    ctx: TenantContext = Depends(get_tenant_context),
    service: AlertService = Depends(get_alert_service),
) -> AlertRead:
    alert = await service.update(
        alert_id=alert_id,
        organization_id=ctx.organization_id,
        payload=payload,
    )
    return AlertRead.model_validate(alert)


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    service: AlertService = Depends(get_alert_service),
) -> None:
    await service.delete(alert_id=alert_id, organization_id=ctx.organization_id)
