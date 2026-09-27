from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db_session
from app.models import User, UserRole
from app.repositories import users as user_repository


bearer = HTTPBearer(auto_error=False)


@lru_cache
def _jwks_client(supabase_url: str) -> PyJWKClient:
    url = f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    return PyJWKClient(url, cache_keys=True)


def _decode_token(token: str, settings: Settings) -> dict:
    settings.validate_auth_configuration()
    assert settings.supabase_url is not None
    try:
        signing_key = _jwks_client(settings.supabase_url).get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "ES256", "EdDSA"],
            audience=settings.supabase_jwt_audience,
            issuer=f"{settings.supabase_url.rstrip('/')}/auth/v1",
        )
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc


def _provision_user(session: Session, claims: dict, settings: Settings) -> User:
    subject = claims.get("sub")
    email = str(claims.get("email", "")).strip().lower()
    if not subject or not email:
        raise HTTPException(status_code=401, detail="Token does not contain user identity")

    user = user_repository.get_by_auth_subject(session, subject)
    if user:
        return user

    roles = {
        settings.admin_email: UserRole.ADMIN,
        settings.member_email: UserRole.MEMBER,
    }
    role = roles.get(email)
    if role is None:
        raise HTTPException(status_code=403, detail="Email is not authorized for this application")

    user = user_repository.get_by_email(session, email)
    if user and user.auth_subject not in (None, subject):
        raise HTTPException(status_code=403, detail="Email is already linked to another identity")
    if user is None:
        metadata = claims.get("user_metadata") or {}
        display_name = metadata.get("display_name") or metadata.get("full_name") or email.split("@", 1)[0]
        user = User(
            auth_subject=subject,
            email=email,
            display_name=str(display_name),
            role=role,
        )
        session.add(user)
    else:
        user.auth_subject = subject
        user.role = role
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        existing = user_repository.get_by_auth_subject(session, subject)
        if existing:
            return existing
        raise
    session.refresh(user)
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: Session = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    claims = _decode_token(credentials.credentials, settings)
    return _provision_user(session, claims, settings)
