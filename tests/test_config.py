from sqlalchemy.engine import make_url

from app.config import Settings


def test_database_url_can_be_built_from_separate_fields() -> None:
    settings = Settings(
        DATABASE_URL=None,
        DATABASE_HOST="pooler.example.com",
        DATABASE_PORT=5432,
        DATABASE_NAME="postgres",
        DATABASE_USER="postgres.project",
        DATABASE_PASSWORD="p@ss/word",
    )

    url = make_url(settings.resolved_database_url())

    assert url.drivername == "postgresql+psycopg"
    assert url.username == "postgres.project"
    assert url.password == "p@ss/word"
    assert url.host == "pooler.example.com"


def test_database_url_still_takes_precedence() -> None:
    settings = Settings(
        DATABASE_URL="postgresql://user:password@localhost/database",
        DATABASE_HOST="ignored.example.com",
        DATABASE_USER="ignored",
        DATABASE_PASSWORD="ignored",
    )

    assert settings.resolved_database_url() == (
        "postgresql+psycopg://user:password@localhost/database"
    )
