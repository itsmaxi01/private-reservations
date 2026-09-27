from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db_session
from app.models import Reservation, User
from app.schemas import ReservationCreate, ReservationRead, ReservationUpdate
from app.services import reservations as service


router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("", response_model=list[ReservationRead])
def list_reservations(
    _: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[Reservation]:
    return service.list_all(session)


@router.get("/upcoming", response_model=list[ReservationRead])
def list_upcoming(
    _: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[Reservation]:
    return service.list_upcoming(session)


@router.post("", response_model=ReservationRead, status_code=status.HTTP_201_CREATED)
def create_reservation(
    data: ReservationCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> Reservation:
    return service.create(session, data, user)


@router.patch("/{reservation_id}", response_model=ReservationRead)
def update_reservation(
    reservation_id: int,
    data: ReservationUpdate,
    _: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> Reservation:
    return service.update(session, reservation_id, data)


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(
    reservation_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> Response:
    service.delete(session, reservation_id, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

