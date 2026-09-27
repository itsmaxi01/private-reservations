from __future__ import annotations

from datetime import date as date_type
from datetime import datetime, time as time_type
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, DateTime, Enum, ForeignKey, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import ReservationType

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.watch_item import WatchItem


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        CheckConstraint(
            "(type = 'DATE' AND title IS NOT NULL AND reason IS NOT NULL "
            "AND watch_item_id IS NULL) OR "
            "(type = 'WATCH' AND title IS NULL AND reason IS NULL "
            "AND watch_item_id IS NOT NULL)",
            name="valid_shape",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[ReservationType] = mapped_column(
        Enum(
            ReservationType,
            native_enum=False,
            create_constraint=True,
            name="reservation_type",
        ),
        index=True,
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[date_type] = mapped_column(Date, index=True)
    time: Mapped[time_type] = mapped_column(Time(timezone=False))
    watch_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("watch_items.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    creator: Mapped[User] = relationship(back_populates="reservations")
    watch_item: Mapped[WatchItem | None] = relationship(back_populates="reservations")
