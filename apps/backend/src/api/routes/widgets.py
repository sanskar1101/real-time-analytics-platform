from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.api.dependencies import TenantContext, get_tenant_context, get_widget_service
from src.schemas.widget import WidgetRead, WidgetUpdate
from src.services.dashboard import WidgetService

router = APIRouter(prefix="/widgets", tags=["Widgets"])


@router.patch("/{widget_id}", response_model=WidgetRead)
async def update_widget(
    widget_id: UUID,
    payload: WidgetUpdate,
    ctx: TenantContext = Depends(get_tenant_context),
    service: WidgetService = Depends(get_widget_service),
) -> WidgetRead:
    widget = await service.update(
        widget_id=widget_id,
        organization_id=ctx.organization_id,
        payload=payload,
    )
    return WidgetRead.model_validate(widget)


@router.delete("/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_widget(
    widget_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    service: WidgetService = Depends(get_widget_service),
) -> None:
    await service.delete(widget_id=widget_id, organization_id=ctx.organization_id)
