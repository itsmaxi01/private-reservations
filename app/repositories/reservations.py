from datetime import date, time

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.models import Reservation, ReservationType


def get(session: Session, reservation_id: int) -> Reservation | None:
    return session.get(Reservation, reservation_id)


def list_all(session: Session) -> list[Reservation]:
    statement = select(Reservation).order_by(Reservation.date, Reservation.time)
    return list(session.scalars(statement))


def list_upcoming(session: Session, today: date, now_time: time) -> list[Reservation]:
    statement = (
        select(Reservation)
        .where(
            or_(
                Reservation.date > today,
                and_(Reservation.date == today, Reservation.time > now_time),
            )
        )
        .order_by(Reservation.date, Reservation.time)
    )
    return list(session.scalars(statement))


def count_dates_between(session: Session, start: date, end: date) -> int:
    statement = select(func.count(Reservation.id)).where(
        Reservation.type == ReservationType.DATE,
        Reservation.date.between(start, end),
    )
    return int(session.scalar(statement) or 0)


def has_future_for_watch_item(
    session: Session,
    watch_item_id: int,
    today: date,
    now_time: time,
) -> bool:
    statement = select(Reservation.id).where(
        Reservation.watch_item_id == watch_item_id,
        or_(
            Reservation.date > today,
            and_(Reservation.date == today, Reservation.time > now_time),
        ),
    )
    return session.scalar(statement.limit(1)) is not None

