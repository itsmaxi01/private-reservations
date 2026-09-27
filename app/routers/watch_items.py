from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db_session
from app.models import User, WatchItem
from app.schemas import WatchItemCreate, WatchItemRead, WatchItemStatusUpdate
from app.services import watch_items as service


router = APIRouter(prefix="/watch-items", tags=["watch-items"])


@router.get("", response_model=list[WatchItemRead])
def list_watch_items(
    _: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[WatchItem]:
    return service.list_active(session)


@router.post("", response_model=WatchItemRead, status_code=status.HTTP_201_CREATED)
def create_watch_item(
    data: WatchItemCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> WatchItem:
    return service.create(session, data, user)


@router.patch("/{watch_item_id}/status", response_model=WatchItemRead)
def set_watch_item_status(
    watch_item_id: int,
    data: WatchItemStatusUpdate,
    _: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> WatchItem:
    return service.set_status(session, watch_item_id, data.status)


@router.post("/{watch_item_id}/archive", response_model=WatchItemRead)
def archive_watch_item(
    watch_item_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> WatchItem:
    return service.archive(session, watch_item_id, user)

