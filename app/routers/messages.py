from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db_session
from app.models import Message, User
from app.schemas import MessageCreate, MessageRead
from app.services import messages as service


router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("", response_model=list[MessageRead])
def list_messages(
    _: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[Message]:
    return service.list_all(session)


@router.post("", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def create_message(
    data: MessageCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> Message:
    return service.create(session, data, user)


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    message_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> Response:
    service.delete(session, message_id, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

