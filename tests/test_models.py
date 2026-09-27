from sqlalchemy import Enum

from app.database import Base
from app.models import Message, Reservation, User, UserRole, WatchItem


def test_expected_tables_are_registered() -> None:
    assert set(Base.metadata.tables) == {
        "messages",
        "reservations",
        "users",
        "watch_items",
    }


def test_reservation_watch_item_is_nullable() -> None:
    assert Reservation.__table__.c.watch_item_id.nullable is True


def test_creator_relationships_are_required() -> None:
    assert Reservation.__table__.c.created_by.nullable is False
    assert WatchItem.__table__.c.added_by.nullable is False
    assert Message.__table__.c.created_by.nullable is False


def test_enums_use_database_check_constraints() -> None:
    assert isinstance(Reservation.__table__.c.type.type, Enum)
    assert Reservation.__table__.c.type.type.native_enum is False


def test_user_has_all_owned_collections() -> None:
    assert set(User.__mapper__.relationships.keys()) == {
        "messages",
        "reservations",
        "watch_items",
    }


def test_new_users_are_members_by_default() -> None:
    assert User.__table__.c.role.default.arg is UserRole.MEMBER


def test_user_email_is_unique_after_normalization() -> None:
    index = next(
        item
        for item in User.__table__.indexes
        if item.name == "uq_users_normalized_email"
    )

    assert index.unique is True


def test_watch_item_title_and_type_are_unique_after_normalization() -> None:
    index = next(
        item
        for item in WatchItem.__table__.indexes
        if item.name == "uq_watch_items_normalized_title_type"
    )

    assert index.unique is True
    assert WatchItem.__table__.c.archived_at.nullable is True
