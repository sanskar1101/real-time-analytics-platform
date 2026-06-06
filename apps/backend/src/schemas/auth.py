from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.schemas.user import UserRead

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class EmailValidatedModel(BaseModel):
    @field_validator("email", check_fields=False)
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if len(normalized) > 320 or EMAIL_PATTERN.fullmatch(normalized) is None:
            raise ValueError("Enter a valid email address.")
        return normalized


class RegisterRequest(EmailValidatedModel):
    organization_name: str = Field(min_length=2, max_length=255)
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("organization_name")
    @classmethod
    def validate_organization_name(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 2:
            raise ValueError("Organization name must contain at least 2 characters.")
        return normalized


class LoginRequest(EmailValidatedModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead
