from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import APIKey


class APIKeyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        api_key_id: UUID,
        organization_id: UUID,
        name: str,
        key_hash: str,
        is_active: bool = True,
    ) -> APIKey:
        api_key = APIKey(
            id=api_key_id,
            organization_id=organization_id,
            name=name,
            key_hash=key_hash,
            is_active=is_active,
        )
        self._session.add(api_key)
        await self._session.flush()
        return api_key

    async def list_by_organization(self, organization_id: UUID) -> list[APIKey]:
        result = await self._session.execute(
            select(APIKey)
            .where(APIKey.organization_id == organization_id)
            .order_by(APIKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_org(self, *, organization_id: UUID, api_key_id: UUID) -> APIKey | None:
        result = await self._session.execute(
            select(APIKey).where(
                APIKey.id == api_key_id,
                APIKey.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_active_by_id(self, api_key_id: UUID) -> APIKey | None:
        result = await self._session.execute(
            select(APIKey).where(
                APIKey.id == api_key_id,
                APIKey.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()
