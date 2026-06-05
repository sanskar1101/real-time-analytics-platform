from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Role, User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        organization_id: UUID,
        email: str,
        password_hash: str,
        role: Role,
        is_active: bool = True,
    ) -> User:
        user = User(
            organization_id=organization_id,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )
        self._session.add(user)
        await self._session.flush()
        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self._session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_org_and_email(self, *, organization_id: UUID, email: str) -> User | None:
        result = await self._session.execute(
            select(User).where(
                User.organization_id == organization_id,
                User.email == email,
            )
        )
        return result.scalar_one_or_none()
