from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Reservation, ReservationType, User, UserRole
from app.repositories import reservations as repository
from app.repositories import watch_items as watch_repository
from app.schemas import ReservationCreate, ReservationUpdate
from app.services.errors import ConflictError, ForbiddenError, NotFoundError, ServiceError


WATCH_DAYS = {0, 2, 4}
WATCH_MINIMUM_TIME = time(22, 40)
DATE_WEEKLY_LIMIT = 2
LOCK_NAMESPACE = 74123


def _local_now() -> datetime:
    return datetime.now(ZoneInfo(get_settings().app_time_zone))


def _ensure_future(reservation_date: date, reservation_time: time) -> None:
    candidate = datetime.combine(reservation_date, reservation_time, tzinfo=_local_now().tzinfo)
    if candidate <= _local_now():
        raise ServiceError("Reservation must be strictly in the future")


def _validate_shape(
    session: Session,
    reservation_type: ReservationType,
    title: str | None,
    reason: str | None,
    watch_item_id: int | None,
    reservation_date: date,
    reservation_time: time,
) -> None:
    _ensure_future(reservation_date, reservation_time)
    if reservation_type is ReservationType.DATE:
        if not title or not reason:
            raise ServiceError("DATE reservations require title and reason")
        if watch_item_id is not None:
            raise ServiceError("DATE reservations cannot reference a WatchItem")
        return

    if title is not None or reason is not None:
        raise ServiceError("WATCH reservations cannot include title or reason")
    if watch_item_id is None:
        raise ServiceError("WATCH reservations require a WatchItem")
    item = watch_repository.get(session, watch_item_id)
    if item is None or item.archived_at is not None:
        raise NotFoundError("Active WatchItem not found")
    if reservation_date.weekday() not in WATCH_DAYS:
        raise ServiceError("WATCH reservations are allowed only Monday, Wednesday or Friday")
    if reservation_time < WATCH_MINIMUM_TIME:
        raise ServiceError("WATCH reservations must start at or after 22:40")


def _lock_and_check_week(session: Session, reservation_date: date) -> None:
    monday = reservation_date - timedelta(days=reservation_date.weekday())
    sunday = monday + timedelta(days=6)
    if session.bind and session.bind.dialect.name == "postgresql":
        session.execute(select(func.pg_advisory_xact_lock(LOCK_NAMESPACE, monday.toordinal())))
    if repository.count_dates_between(session, monday, sunday) >= DATE_WEEKLY_LIMIT:
        raise ConflictError("The global weekly DATE reservation limit has been reached")


def create(session: Session, data: ReservationCreate, actor: User) -> Reservation:
    _validate_shape(session, data.type, data.title, data.reason, data.watch_item_id, data.date, data.time)
    if data.type is ReservationType.DATE:
        _lock_and_check_week(session, data.date)
    reservation = Reservation(**data.model_dump(), created_by=actor.id)
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation


def update(
    session: Session,
    reservation_id: int,
    data: ReservationUpdate,
) -> Reservation:
    reservation = repository.get(session, reservation_id)
    if reservation is None:
        raise NotFoundError("Reservation not found")
    _ensure_future(reservation.date, reservation.time)
    changes = data.model_dump(exclude_unset=True)
    if "type" in changes:
        raise ServiceError("Reservation type cannot be changed")
    values = {
        "title": changes.get("title", reservation.title),
        "reason": changes.get("reason", reservation.reason),
        "date": changes.get("date", reservation.date),
        "time": changes.get("time", reservation.time),
        "watch_item_id": changes.get("watch_item_id", reservation.watch_item_id),
    }
    _validate_shape(
        session,
        reservation.type,
        values["title"],
        values["reason"],
        values["watch_item_id"],
        values["date"],
        values["time"],
    )
    old_monday = reservation.date - timedelta(days=reservation.date.weekday())
    new_monday = values["date"] - timedelta(days=values["date"].weekday())
    if reservation.type is ReservationType.DATE and old_monday != new_monday:
        _lock_and_check_week(session, values["date"])
    for field, value in changes.items():
        setattr(reservation, field, value)
    session.commit()
    session.refresh(reservation)
    return reservation


def delete(session: Session, reservation_id: int, actor: User) -> None:
    if actor.role is not UserRole.ADMIN:
        raise ForbiddenError("Only ADMIN can delete reservations")
    reservation = repository.get(session, reservation_id)
    if reservation is None:
        raise NotFoundError("Reservation not found")
    session.delete(reservation)
    session.commit()


def list_all(session: Session) -> list[Reservation]:
    return repository.list_all(session)


def list_upcoming(session: Session) -> list[Reservation]:
    now = _local_now()
    return repository.list_upcoming(session, now.date(), now.time().replace(tzinfo=None))
