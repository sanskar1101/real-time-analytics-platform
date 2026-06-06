from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field, computed_field

BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"


def load_env_file(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


class Settings(BaseModel):
    app_name: str = Field(default="Real-Time Analytics Platform")
    environment: str = Field(default="development")
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/real_time_analysis"
    )
    redis_url: str = Field(default="redis://localhost:6379/0")
    jwt_secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=15, ge=1)
    refresh_token_expire_days: int = Field(default=30, ge=1)
    cors_origins: list[str] = Field(default=["http://localhost:3000"])
    allowed_hosts: list[str] = Field(default=["*"])
    reports_dir: str = Field(default=str(BACKEND_DIR / "reports"))

    @computed_field
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @classmethod
    def from_env(cls) -> Settings:
        load_env_file()

        raw_cors = os.getenv("CORS_ORIGINS", "")
        cors_origins = (
            [o.strip() for o in raw_cors.split(",") if o.strip()]
            if raw_cors
            else cls.model_fields["cors_origins"].default
        )

        raw_hosts = os.getenv("ALLOWED_HOSTS", "")
        allowed_hosts = (
            [h.strip() for h in raw_hosts.split(",") if h.strip()]
            if raw_hosts
            else cls.model_fields["allowed_hosts"].default
        )

        db_url = os.getenv("DATABASE_URL", cls.model_fields["database_url"].default)
        # Render provides plain postgresql:// DSN; asyncpg requires the +asyncpg driver prefix.
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        settings = cls(
            app_name=os.getenv("APP_NAME", cls.model_fields["app_name"].default),
            environment=os.getenv("ENVIRONMENT", cls.model_fields["environment"].default),
            database_url=db_url,
            redis_url=os.getenv("REDIS_URL", cls.model_fields["redis_url"].default),
            jwt_secret_key=os.getenv(
                "JWT_SECRET_KEY",
                os.getenv("SECRET_KEY", cls.model_fields["jwt_secret_key"].default),
            ),
            jwt_algorithm=os.getenv(
                "JWT_ALGORITHM",
                os.getenv("ALGORITHM", cls.model_fields["jwt_algorithm"].default),
            ),
            access_token_expire_minutes=int(
                os.getenv(
                    "ACCESS_TOKEN_EXPIRE_MINUTES",
                    str(cls.model_fields["access_token_expire_minutes"].default),
                )
            ),
            refresh_token_expire_days=int(
                os.getenv(
                    "REFRESH_TOKEN_EXPIRE_DAYS",
                    str(cls.model_fields["refresh_token_expire_days"].default),
                )
            ),
            cors_origins=cors_origins,
            allowed_hosts=allowed_hosts,
            reports_dir=os.getenv("REPORTS_DIR", cls.model_fields["reports_dir"].default),
        )
        if settings.is_production and settings.jwt_secret_key == "change-me-in-production":
            raise RuntimeError("JWT_SECRET_KEY must be set in production.")
        return settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()


settings = get_settings()
