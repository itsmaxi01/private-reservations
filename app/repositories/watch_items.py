from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ContentType, WatchItem


def get(session: Session, watch_item_id: int) -> WatchItem | None:
    return session.get(WatchItem, watch_item_id)


def find_duplicate(session: Session, title: str, content_type: ContentType) -> WatchItem | None:
    normalized = title.strip().lower()
    statement = select(WatchItem).where(
        func.lower(func.btrim(WatchItem.title)) == normalized,
        WatchItem.type == content_type,
    )
    return session.scalar(statement)


def list_active(session: Session) -> list[WatchItem]:
    statement = (
        select(WatchItem)
        .where(WatchItem.archived_at.is_(None))
        .order_by(WatchItem.created_at.desc())
    )
    return list(session.scalars(statement))

