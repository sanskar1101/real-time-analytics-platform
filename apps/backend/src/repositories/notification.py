from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.notification import Notification


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        organization_id: UUID,
        title: str,
        message: str,
    ) -> Notification:
        notification = Notification(
            organization_id=organization_id,
            title=title,
            message=message,
        )
        self._session.add(notification)
        await self._session.flush()
        return notification

    async def get_by_id_and_org(
        self,
        *,
        notification_id: UUID,
        organization_id: UUID,
    ) -> Notification | None:
        stmt = select(Notification).where(
            Notification.id == notification_id,
            Notification.organization_id == organization_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_organization(
        self,
        *,
        organization_id: UUID,
        limit: int,
        offset: int,
        unread_only: bool = False,
    ) -> tuple[list[Notification], int]:
        base_where = [Notification.organization_id == organization_id]
        if unread_only:
            base_where.append(Notification.is_read.is_(False))

        count_stmt = select(func.count()).select_from(Notification).where(*base_where)
        total: int = (await self._session.execute(count_stmt)).scalar_one()

        stmt = (
            select(Notification)
            .where(*base_where)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return list(rows), total
