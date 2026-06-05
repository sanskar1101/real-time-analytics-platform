from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.notification import Notification
from src.repositories.notification import NotificationRepository
from src.schemas.notification import NotificationRead, PaginatedNotifications


class NotificationService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        notification_repository: NotificationRepository,
    ) -> None:
        self._session = session
        self._notifications = notification_repository

    async def list(
        self,
        *,
        organization_id: UUID,
        limit: int,
        offset: int,
        unread_only: bool = False,
    ) -> PaginatedNotifications:
        items, total = await self._notifications.list_by_organization(
            organization_id=organization_id,
            limit=limit,
            offset=offset,
            unread_only=unread_only,
        )
        return PaginatedNotifications(
            items=[NotificationRead.model_validate(n) for n in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def mark_read(
        self,
        *,
        notification_id: UUID,
        organization_id: UUID,
    ) -> Notification:
        notification = await self._notifications.get_by_id_and_org(
            notification_id=notification_id,
            organization_id=organization_id,
        )
        if notification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found.",
            )
        notification.is_read = True
        await self._session.commit()
        return notification
