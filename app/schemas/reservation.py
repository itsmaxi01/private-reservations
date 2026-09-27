from datetime import date as date_type
from datetime import datetime, time as time_type

from pydantic import BaseModel, field_validator, model_validator

from app.models.enums import ReservationType
from app.schemas.common import NonEmptyStr, ReadSchema


class ReservationCreate(BaseModel):
    type: ReservationType
    title: NonEmptyStr | None = None
    reason: NonEmptyStr | None = None
    date: date_type
    time: time_type
    watch_item_id: int | None = None

    @model_validator(mode="after")
    def watch_reservation_rejects_date_fields(self) -> "ReservationCreate":
        if self.type is ReservationType.WATCH and (
            self.title is not None or self.reason is not None
        ):
            raise ValueError("WATCH reservations cannot include title or reason")
        return self


class ReservationUpdate(BaseModel):
    type: ReservationType | None = None
    title: NonEmptyStr | None = None
    reason: NonEmptyStr | None = None
    date: date_type | None = None
    time: time_type | None = None
    watch_item_id: int | None = None

    @field_validator("type", "date", "time")
    @classmethod
    def required_fields_cannot_be_cleared(cls, value: object | None) -> object:
        if value is None:
            raise ValueError("field cannot be null")
        return value


class ReservationRead(ReadSchema):
    id: int
    type: ReservationType
    title: str | None
    reason: str | None
    date: date_type
    time: time_type
    watch_item_id: int | None
    created_by: int
    created_at: datetime
