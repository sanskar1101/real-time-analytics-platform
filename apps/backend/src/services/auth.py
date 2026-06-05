from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from src.models import Role, User
from src.repositories import OrganizationRepository, UserRepository
from src.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(
        self,
        *,
        session: AsyncSession,
        user_repository: UserRepository,
        organization_repository: OrganizationRepository,
    ) -> None:
        self._session = session
        self._users = user_repository
        self._organizations = organization_repository

    async def register(self, payload: RegisterRequest) -> TokenResponse:
        normalized_email = payload.email.lower()
        organization_name = payload.organization_name.strip()

        if await self._users.get_by_email(normalized_email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        if await self._organizations.get_by_name(organization_name) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An organization with this name already exists.",
            )

        try:
            organization = await self._organizations.create(name=organization_name)
            user = await self._users.create(
                organization_id=organization.id,
                email=normalized_email,
                password_hash=hash_password(payload.password),
                role=Role.OWNER,
            )
            user.organization = organization
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Registration conflicts with an existing account.",
            ) from exc

        return self._build_token_response(user)

    async def login(self, payload: LoginRequest) -> TokenResponse:
        user = await self._users.get_by_email(payload.email.lower())
        if (
            user is None
            or not user.is_active
            or not verify_password(payload.password, user.password_hash)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return self._build_token_response(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token, expected_token_type="refresh")
        subject = payload.get("sub")
        if subject is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await self._users.get_by_id(UUID(subject))
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_org = payload.get("org")
        if token_org != str(user.organization_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return self._build_token_response(user)

    @staticmethod
    def _build_token_response(user: User) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(
                subject=user.id,
                organization_id=user.organization_id,
                role=user.role.value,
            ),
            refresh_token=create_refresh_token(
                subject=user.id,
                organization_id=user.organization_id,
            ),
            expires_in=settings.access_token_expire_minutes * 60,
            user=user,
        )
