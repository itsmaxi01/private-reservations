import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth import _provision_user
from app.config import Settings
from app.models import UserRole


def auth_settings() -> Settings:
    return Settings(
        DATABASE_URL="postgresql+psycopg://test:test@localhost/test",
        SUPABASE_URL="https://example.supabase.co",
        SUPABASE_PUBLISHABLE_KEY="publishable",
        ADMIN_EMAIL="admin@example.com",
        MEMBER_EMAIL="member@example.com",
    )


def test_allowed_email_is_provisioned_with_configured_role(session: Session) -> None:
    user = _provision_user(
        session,
        {"sub": "supabase-user-1", "email": "ADMIN@EXAMPLE.COM"},
        auth_settings(),
    )

    assert user.role is UserRole.ADMIN
    assert user.email == "admin@example.com"
    assert user.auth_subject == "supabase-user-1"


def test_unknown_email_cannot_be_provisioned(session: Session) -> None:
    with pytest.raises(HTTPException) as error:
        _provision_user(
            session,
            {"sub": "intruder", "email": "other@example.com"},
            auth_settings(),
        )

    assert error.value.status_code == 403
