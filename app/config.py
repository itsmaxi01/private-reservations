from functools import lru_cache
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    database_url: str = Field(validation_alias="DATABASE_URL")
    app_time_zone: str = Field(
        default="America/Mexico_City",
        validation_alias="APP_TIME_ZONE",
    )
    supabase_url: str | None = Field(default=None, validation_alias="SUPABASE_URL")
    supabase_publishable_key: str | None = Field(
        default=None,
        validation_alias="SUPABASE_PUBLISHABLE_KEY",
    )
    supabase_jwt_audience: str = Field(
        default="authenticated",
        validation_alias="SUPABASE_JWT_AUDIENCE",
    )
    admin_email: str | None = Field(default=None, validation_alias="ADMIN_EMAIL")
    member_email: str | None = Field(default=None, validation_alias="MEMBER_EMAIL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("database_url")
    @classmethod
    def database_url_must_use_postgresql(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        if not value.startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL must be a PostgreSQL URL using psycopg")
        return value

    @field_validator("app_time_zone")
    @classmethod
    def time_zone_must_exist(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("APP_TIME_ZONE must be a valid IANA time zone") from exc
        return value

    @field_validator("admin_email", "member_email")
    @classmethod
    def normalize_optional_email(cls, value: str | None) -> str | None:
        return value.strip().lower() if value else None

    def validate_auth_configuration(self) -> None:
        required = {
            "SUPABASE_URL": self.supabase_url,
            "SUPABASE_PUBLISHABLE_KEY": self.supabase_publishable_key,
            "ADMIN_EMAIL": self.admin_email,
            "MEMBER_EMAIL": self.member_email,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(f"Missing authentication settings: {', '.join(missing)}")
        if self.admin_email == self.member_email:
            raise RuntimeError("ADMIN_EMAIL and MEMBER_EMAIL must be different")


@lru_cache
def get_settings() -> Settings:
    return Settings()
