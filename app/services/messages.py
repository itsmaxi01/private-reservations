from sqlalchemy.orm import Session

from app.models import Message, User, UserRole
from app.repositories import messages as repository
from app.schemas import MessageCreate
from app.services.errors import ForbiddenError, NotFoundError


def create(session: Session, data: MessageCreate, actor: User) -> Message:
    message = Message(**data.model_dump(), created_by=actor.id)
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


def list_all(session: Session) -> list[Message]:
    return repository.list_all(session)


def delete(session: Session, message_id: int, actor: User) -> None:
    if actor.role is not UserRole.ADMIN:
        raise ForbiddenError("Only ADMIN can delete messages")
    message = repository.get(session, message_id)
    if message is None:
        raise NotFoundError("Message not found")
    session.delete(message)
    session.commit()

