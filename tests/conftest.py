import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.config import get_settings
from app.models import User, UserRole


@pytest.fixture(autouse=True)
def test_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost/test")
    monkeypatch.setenv("APP_TIME_ZONE", "America/Mexico_City")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def add_functions(connection, _record) -> None:
        connection.create_function(
            "btrim",
            1,
            lambda value: value.strip(),
            deterministic=True,
        )

    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as database_session:
        yield database_session
    Base.metadata.drop_all(engine)


@pytest.fixture
def admin(session: Session) -> User:
    user = User(email="admin@example.com", display_name="Admin", role=UserRole.ADMIN)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def member(session: Session) -> User:
    user = User(email="member@example.com", display_name="Member", role=UserRole.MEMBER)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
