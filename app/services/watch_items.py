from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import User, UserRole, WatchItem, WatchStatus
from app.repositories import reservations as reservation_repository
from app.repositories import watch_items as repository
from app.schemas import WatchItemCreate
from app.services.errors import ConflictError, ForbiddenError, NotFoundError


def create(session: Session, data: WatchItemCreate, actor: User) -> WatchItem:
    if repository.find_duplicate(session, data.title, data.type):
        raise ConflictError("A WatchItem with the same normalized title and type already exists")
    item = WatchItem(**data.model_dump(), added_by=actor.id)
    session.add(item)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise ConflictError(
            "A WatchItem with the same normalized title and type already exists"
        ) from exc
    session.refresh(item)
    return item


def set_status(
    session: Session,
    watch_item_id: int,
    status: WatchStatus,
) -> WatchItem:
    item = repository.get(session, watch_item_id)
    if item is None or item.archived_at is not None:
        raise NotFoundError("Active WatchItem not found")
    item.status = status
    session.commit()
    session.refresh(item)
    return item


def archive(session: Session, watch_item_id: int, actor: User) -> WatchItem:
    if actor.role is not UserRole.ADMIN:
        raise ForbiddenError("Only ADMIN can archive WatchItems")
    item = repository.get(session, watch_item_id)
    if item is None or item.archived_at is not None:
        raise NotFoundError("Active WatchItem not found")
    now = datetime.now(ZoneInfo(get_settings().app_time_zone))
    if reservation_repository.has_future_for_watch_item(
        session, item.id, now.date(), now.time().replace(tzinfo=None)
    ):
        raise ConflictError("A WatchItem with future reservations cannot be archived")
    item.archived_at = now
    session.commit()
    session.refresh(item)
    return item


def list_active(session: Session) -> list[WatchItem]:
    return repository.list_active(session)
