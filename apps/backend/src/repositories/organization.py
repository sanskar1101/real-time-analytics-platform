from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Organization


class OrganizationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, name: str) -> Organization:
        organization = Organization(name=name)
        self._session.add(organization)
        await self._session.flush()
        return organization

    async def get_by_id(self, organization_id: UUID) -> Organization | None:
        return await self._session.get(Organization, organization_id)

    async def get_by_name(self, name: str) -> Organization | None:
        result = await self._session.execute(select(Organization).where(Organization.name == name))
        return result.scalar_one_or_none()
