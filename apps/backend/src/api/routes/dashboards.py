from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import (
    TenantContext,
    get_dashboard_service,
    get_tenant_context,
    get_widget_service,
)
from src.schemas.dashboard import (
    DashboardCreate,
    DashboardRead,
    DashboardUpdate,
    PaginatedDashboards,
)
from src.schemas.widget import WidgetCreate, WidgetRead
from src.services.dashboard import DashboardService, WidgetService

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])


@router.post("", response_model=DashboardRead, status_code=status.HTTP_201_CREATED)
async def create_dashboard(
    payload: DashboardCreate,
    ctx: TenantContext = Depends(get_tenant_context),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardRead:
    dashboard = await service.create(organization_id=ctx.organization_id, payload=payload)
    return DashboardRead.model_validate(dashboard)


@router.get("", response_model=PaginatedDashboards)
async def list_dashboards(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    ctx: TenantContext = Depends(get_tenant_context),
    service: DashboardService = Depends(get_dashboard_service),
) -> PaginatedDashboards:
    return await service.list(
        organization_id=ctx.organization_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{dashboard_id}", response_model=DashboardRead)
async def get_dashboard(
    dashboard_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardRead:
    dashboard = await service.get(
        dashboard_id=dashboard_id,
        organization_id=ctx.organization_id,
    )
    return DashboardRead.model_validate(dashboard)


@router.patch("/{dashboard_id}", response_model=DashboardRead)
async def update_dashboard(
    dashboard_id: UUID,
    payload: DashboardUpdate,
    ctx: TenantContext = Depends(get_tenant_context),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardRead:
    dashboard = await service.update(
        dashboard_id=dashboard_id,
        organization_id=ctx.organization_id,
        payload=payload,
    )
    return DashboardRead.model_validate(dashboard)


@router.delete("/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dashboard(
    dashboard_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    service: DashboardService = Depends(get_dashboard_service),
) -> None:
    await service.delete(dashboard_id=dashboard_id, organization_id=ctx.organization_id)


@router.post(
    "/{dashboard_id}/widgets",
    response_model=WidgetRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_widget(
    dashboard_id: UUID,
    payload: WidgetCreate,
    ctx: TenantContext = Depends(get_tenant_context),
    service: WidgetService = Depends(get_widget_service),
) -> WidgetRead:
    widget = await service.create(
        dashboard_id=dashboard_id,
        organization_id=ctx.organization_id,
        payload=payload,
    )
    return WidgetRead.model_validate(widget)


@router.get("/{dashboard_id}/widgets", response_model=list[WidgetRead])
async def list_widgets(
    dashboard_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    service: WidgetService = Depends(get_widget_service),
) -> list[WidgetRead]:
    widgets = await service.list(
        dashboard_id=dashboard_id,
        organization_id=ctx.organization_id,
    )
    return [WidgetRead.model_validate(w) for w in widgets]
