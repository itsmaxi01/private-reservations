from datetime import date, time

import pytest
from sqlalchemy.orm import Session

from app.models import ContentType, ReservationType, User, WatchStatus
from app.schemas import MessageCreate, ReservationCreate, WatchItemCreate
from app.services import messages, reservations, watch_items
from app.services.errors import ConflictError, ForbiddenError


def date_payload(day: int, title: str) -> ReservationCreate:
    return ReservationCreate(
        type=ReservationType.DATE,
        title=title,
        reason="Porque sí",
        date=date(2035, 1, day),
        time=time(20, 0),
    )


def test_weekly_date_limit_is_global(session: Session, admin: User, member: User) -> None:
    reservations.create(session, date_payload(1, "Primera"), admin)
    reservations.create(session, date_payload(3, "Segunda"), member)

    with pytest.raises(ConflictError):
        reservations.create(session, date_payload(7, "Tercera"), admin)


def test_watched_item_can_be_reserved(session: Session, admin: User) -> None:
    item = watch_items.create(
        session,
        WatchItemCreate(title="Frieren", type=ContentType.ANIME, status=WatchStatus.WATCHED),
        admin,
    )
    created = reservations.create(
        session,
        ReservationCreate(
            type=ReservationType.WATCH,
            date=date(2035, 1, 3),  # Wednesday
            time=time(22, 40),
            watch_item_id=item.id,
        ),
        admin,
    )

    assert created.watch_item_id == item.id


def test_member_cannot_delete_message(session: Session, admin: User, member: User) -> None:
    message = messages.create(session, MessageCreate(content="Hola"), admin)

    with pytest.raises(ForbiddenError):
        messages.delete(session, message.id, member)


def test_duplicate_watch_item_is_rejected(session: Session, admin: User) -> None:
    watch_items.create(session, WatchItemCreate(title="  Dune  ", type=ContentType.MOVIE), admin)

    with pytest.raises(ConflictError):
        watch_items.create(session, WatchItemCreate(title="dUnE", type=ContentType.MOVIE), admin)
