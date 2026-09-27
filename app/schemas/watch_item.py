from datetime import datetime

from pydantic import BaseModel, field_validator

from app.models.enums import ContentType, WatchStatus
from app.schemas.common import NonEmptyStr, ReadSchema


class WatchItemCreate(BaseModel):
    title: NonEmptyStr
    type: ContentType
    status: WatchStatus = WatchStatus.PENDING


class WatchItemUpdate(BaseModel):
    title: NonEmptyStr | None = None
    type: ContentType | None = None
    status: WatchStatus | None = None

    @field_validator("title", "type", "status")
    @classmethod
    def required_fields_cannot_be_cleared(cls, value: object | None) -> object:
        if value is None:
            raise ValueError("field cannot be null")
        return value


class WatchItemStatusUpdate(BaseModel):
    status: WatchStatus


class WatchItemRead(ReadSchema):
    id: int
    title: str
    type: ContentType
    status: WatchStatus
    added_by: int
    created_at: datetime
    archived_at: datetime | None
