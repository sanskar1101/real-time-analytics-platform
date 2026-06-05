from __future__ import annotations

import uuid
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import generate_api_key, hash_api_key
from src.models import APIKey
from src.repositories import APIKeyRepository
from src.schemas.api_key import APIKeyCreate, APIKeyCreated, APIKeyRead, APIKeyRotated


class APIKeyService:
    def __init__(self, *, session: AsyncSession, api_key_repository: APIKeyRepository) -> None:
        self._session = session
        self._api_keys = api_key_repository

    async def create(self, *, organization_id: UUID, payload: APIKeyCreate) -> APIKeyCreated:
        api_key_id = uuid.uuid4()
        raw_key = generate_api_key(api_key_id)
        api_key = await self._api_keys.create(
            api_key_id=api_key_id,
            organization_id=organization_id,
            name=payload.name.strip(),
            key_hash=hash_api_key(raw_key),
        )
        await self._session.commit()
        return APIKeyCreated(
            **APIKeyRead.model_validate(api_key).model_dump(),
            key=raw_key,
        )

    async def list(self, *, organization_id: UUID) -> list[APIKey]:
        return await self._api_keys.list_by_organization(organization_id)

    async def delete(self, *, organization_id: UUID, api_key_id: UUID) -> None:
        api_key = await self._get_org_key(organization_id=organization_id, api_key_id=api_key_id)
        api_key.is_active = False
        await self._session.commit()

    async def rotate(self, *, organization_id: UUID, api_key_id: UUID) -> APIKeyRotated:
        api_key = await self._get_org_key(organization_id=organization_id, api_key_id=api_key_id)
        raw_key = generate_api_key(api_key.id)
        api_key.key_hash = hash_api_key(raw_key)
        api_key.is_active = True
        await self._session.commit()
        return APIKeyRotated(id=api_key.id, key=raw_key)

    async def _get_org_key(self, *, organization_id: UUID, api_key_id: UUID) -> APIKey:
        api_key = await self._api_keys.get_by_org(
            organization_id=organization_id,
            api_key_id=api_key_id,
        )
        if api_key is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found.",
            )
        return api_key
