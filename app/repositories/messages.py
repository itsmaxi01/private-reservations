from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Message


def get(session: Session, message_id: int) -> Message | None:
    return session.get(Message, message_id)


def list_all(session: Session) -> list[Message]:
    statement = select(Message).order_by(Message.is_pinned.desc(), Message.created_at.desc())
    return list(session.scalars(statement))

