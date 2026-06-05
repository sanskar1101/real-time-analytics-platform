from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import TenantContext, get_notification_service, get_tenant_context
from src.schemas.notification import NotificationRead, PaginatedNotifications
from src.services.notification import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=PaginatedNotifications)
async def list_notifications(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    unread_only: bool = Query(default=False),
    ctx: TenantContext = Depends(get_tenant_context),
    service: NotificationService = Depends(get_notification_service),
) -> PaginatedNotifications:
    return await service.list(
        organization_id=ctx.organization_id,
        limit=limit,
        offset=offset,
        unread_only=unread_only,
    )


@router.patch("/{notification_id}/read", response_model=NotificationRead)
async def mark_notification_read(
    notification_id: UUID,
    ctx: TenantContext = Depends(get_tenant_context),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationRead:
    notification = await service.mark_read(
        notification_id=notification_id,
        organization_id=ctx.organization_id,
    )
    return NotificationRead.model_validate(notification)
