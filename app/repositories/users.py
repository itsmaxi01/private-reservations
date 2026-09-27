from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


def get_by_auth_subject(session: Session, subject: str) -> User | None:
    return session.scalar(select(User).where(User.auth_subject == subject))


def get_by_email(session: Session, email: str) -> User | None:
    normalized = email.strip().lower()
    return session.scalar(select(User).where(User.email == normalized))

