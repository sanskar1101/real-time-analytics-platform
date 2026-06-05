from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import decode_token, parse_api_key_id, verify_api_key
from src.db.session import get_async_session
from src.models import APIKey, Role, User
from src.repositories import APIKeyRepository, EventRepository, OrganizationRepository, UserRepository
from src.services import APIKeyService, EventIngestionService
from src.services.auth import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


@dataclass(frozen=True, slots=True)
class TenantContext:
    organization_id: UUID
    user_id: UUID
    role: Role


def get_user_repository(
    session: AsyncSession = Depends(get_async_session),
) -> UserRepository:
    return UserRepository(session)


def get_organization_repository(
    session: AsyncSession = Depends(get_async_session),
) -> OrganizationRepository:
    return OrganizationRepository(session)


def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuthService:
    return AuthService(
        session=session,
        user_repository=UserRepository(session),
        organization_repository=OrganizationRepository(session),
    )


def get_api_key_service(
    session: AsyncSession = Depends(get_async_session),
) -> APIKeyService:
    return APIKeyService(
        session=session,
        api_key_repository=APIKeyRepository(session),
    )


def get_event_ingestion_service(
    session: AsyncSession = Depends(get_async_session),
) -> EventIngestionService:
    return EventIngestionService(
        session=session,
        event_repository=EventRepository(session),
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    users: UserRepository = Depends(get_user_repository),
) -> User:
    payload = decode_token(token, expected_token_type="access")
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await users.get_by_id(UUID(user_id))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_tenant_context(
    current_user: User = Depends(get_current_user),
) -> TenantContext:
    return TenantContext(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        role=current_user.role,
    )


async def get_current_api_key(
    raw_api_key: str | None = Depends(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> APIKey:
    if raw_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required.",
        )

    api_key_id = parse_api_key_id(raw_api_key)
    if api_key_id is not None:
        api_key = await APIKeyRepository(session).get_active_by_id(api_key_id)
        if api_key is not None and verify_api_key(raw_api_key, api_key.key_hash):
            return api_key

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key.",
    )
