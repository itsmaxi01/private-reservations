from datetime import date, time

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db_session
from app.main import app
from app.models import User


def make_client(session: Session, user: User | None = None) -> TestClient:
    def override_session():
        yield session

    app.dependency_overrides[get_db_session] = override_session
    if user is not None:
        app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app)


def test_protected_endpoint_requires_authentication(session: Session) -> None:
    with make_client(session) as client:
        response = client.get("/api/messages")
    app.dependency_overrides.clear()

    assert response.status_code == 401


def test_authenticated_user_can_create_date_reservation(
    session: Session,
    admin: User,
) -> None:
    payload = {
        "type": "DATE",
        "title": "Cena",
        "reason": "Aniversario",
        "date": date(2035, 2, 1).isoformat(),
        "time": time(20, 0).isoformat(),
    }
    with make_client(session, admin) as client:
        response = client.post("/api/reservations", json=payload)
    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["created_by"] == admin.id


def test_frontend_is_served(session: Session) -> None:
    with make_client(session) as client:
        response = client.get("/")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Nuestro espacio" in response.text
