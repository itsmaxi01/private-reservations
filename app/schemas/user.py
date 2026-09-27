from datetime import datetime

from pydantic import BaseModel, field_validator

from app.models.enums import UserRole
from app.schemas.common import NonEmptyStr, ReadSchema


class UserCreate(BaseModel):
    email: NonEmptyStr
    display_name: NonEmptyStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class UserUpdate(BaseModel):
    email: NonEmptyStr | None = None
    display_name: NonEmptyStr | None = None

    @field_validator("email")
    @classmethod
    def normalize_updated_email(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("field cannot be null")
        return value.lower()

    @field_validator("display_name")
    @classmethod
    def display_name_cannot_be_cleared(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("field cannot be null")
        return value


class UserRead(ReadSchema):
    id: int
    email: str
    display_name: str
    role: UserRole
    created_at: datetime
