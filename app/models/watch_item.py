from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import ContentType, WatchStatus

if TYPE_CHECKING:
    from app.models.reservation import Reservation
    from app.models.user import User


class WatchItem(Base):
    __tablename__ = "watch_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    type: Mapped[ContentType] = mapped_column(
        Enum(
            ContentType,
            native_enum=False,
            create_constraint=True,
            name="content_type",
        )
    )
    status: Mapped[WatchStatus] = mapped_column(
        Enum(
            WatchStatus,
            native_enum=False,
            create_constraint=True,
            name="watch_status",
        ),
        default=WatchStatus.PENDING,
        server_default=WatchStatus.PENDING.value,
    )
    added_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index(
            "uq_watch_items_normalized_title_type",
            func.lower(func.btrim(title)),
            type,
            unique=True,
        ),
    )

    added_by_user: Mapped[User] = relationship(back_populates="watch_items")
    reservations: Mapped[list[Reservation]] = relationship(back_populates="watch_item")
