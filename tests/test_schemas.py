from datetime import date, time

import pytest
from pydantic import ValidationError

from app.models.enums import ReservationType
from app.schemas import (
    MessageCreate,
    ReservationCreate,
    ReservationUpdate,
    UserUpdate,
    WatchItemCreate,
)


def test_message_content_cannot_be_blank() -> None:
    with pytest.raises(ValidationError):
        MessageCreate(content="   ")


def test_create_schemas_do_not_accept_creator_ids() -> None:
    assert "created_by" not in MessageCreate.model_fields
    assert "added_by" not in WatchItemCreate.model_fields


def test_update_can_be_empty_but_required_field_cannot_be_cleared() -> None:
    assert UserUpdate().model_dump(exclude_unset=True) == {}

    with pytest.raises(ValidationError):
        UserUpdate(email=None)


def test_user_email_is_normalized() -> None:
    user = UserUpdate(email="  PERSON@EXAMPLE.COM  ")

    assert user.email == "person@example.com"


def test_nullable_reservation_field_can_be_explicitly_cleared() -> None:
    update = ReservationUpdate(watch_item_id=None)

    assert update.model_dump(exclude_unset=True) == {"watch_item_id": None}


@pytest.mark.parametrize("field", ["title", "reason"])
def test_watch_reservation_rejects_date_fields(field: str) -> None:
    payload = {
        "type": ReservationType.WATCH,
        "date": date(2030, 1, 2),
        "time": time(22, 40),
        "watch_item_id": 1,
        field: "not allowed",
    }

    with pytest.raises(ValidationError):
        ReservationCreate.model_validate(payload)
