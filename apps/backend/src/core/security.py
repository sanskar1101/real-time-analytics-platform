from __future__ import annotations

from datetime import datetime, timedelta, timezone
import secrets
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import settings

password_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    pbkdf2_sha256__rounds=390000,
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return password_context.verify(plain_password, password_hash)


def generate_api_key(key_id: UUID) -> str:
    return f"rta_{key_id.hex}_{secrets.token_urlsafe(32)}"


def parse_api_key_id(api_key: str) -> UUID | None:
    parts = api_key.split("_", 2)
    if len(parts) != 3 or parts[0] != "rta":
        return None

    try:
        return UUID(hex=parts[1])
    except ValueError:
        return None


def hash_api_key(api_key: str) -> str:
    return password_context.hash(api_key)


def verify_api_key(api_key: str, key_hash: str) -> bool:
    return password_context.verify(api_key, key_hash)


def create_token(
    *,
    subject: UUID,
    organization_id: UUID,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "org": str(organization_id),
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": now + expires_delta,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(*, subject: UUID, organization_id: UUID, role: str) -> str:
    return create_token(
        subject=subject,
        organization_id=organization_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        extra_claims={"role": role},
    )


def create_refresh_token(*, subject: UUID, organization_id: UUID) -> str:
    return create_token(
        subject=subject,
        organization_id=organization_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str, *, expected_token_type: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if payload.get("type") != expected_token_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
