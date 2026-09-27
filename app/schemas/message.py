from datetime import datetime

from pydantic import BaseModel, field_validator

from app.schemas.common import NonEmptyStr, ReadSchema


class MessageCreate(BaseModel):
    content: NonEmptyStr
    is_pinned: bool = False


class MessageUpdate(BaseModel):
    content: NonEmptyStr | None = None
    is_pinned: bool | None = None

    @field_validator("content", "is_pinned")
    @classmethod
    def required_fields_cannot_be_cleared(cls, value: object | None) -> object:
        if value is None:
            raise ValueError("field cannot be null")
        return value


class MessageRead(ReadSchema):
    id: int
    content: str
    created_by: int
    is_pinned: bool
    created_at: datetime
