from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.message import Message
    from app.models.reservation import Reservation
    from app.models.watch_item import WatchItem


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    auth_subject: Mapped[str | None] = mapped_column(
        String(128),
        unique=True,
        nullable=True,
    )
    email: Mapped[str] = mapped_column(String(320))
    display_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            native_enum=False,
            create_constraint=True,
            name="user_role",
        ),
        default=UserRole.MEMBER,
        server_default=UserRole.MEMBER.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        Index(
            "uq_users_normalized_email",
            func.lower(func.btrim(email)),
            unique=True,
        ),
    )

    reservations: Mapped[list[Reservation]] = relationship(back_populates="creator")
    watch_items: Mapped[list[WatchItem]] = relationship(back_populates="added_by_user")
    messages: Mapped[list[Message]] = relationship(back_populates="creator")
