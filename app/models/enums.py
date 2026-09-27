from enum import StrEnum


class ReservationType(StrEnum):
    DATE = "DATE"
    WATCH = "WATCH"


class ContentType(StrEnum):
    MOVIE = "MOVIE"
    ANIME = "ANIME"


class WatchStatus(StrEnum):
    PENDING = "PENDING"
    WATCHED = "WATCHED"


class UserRole(StrEnum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
