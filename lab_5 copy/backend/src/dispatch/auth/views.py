from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from src.dispatch.auth import service as auth_service
from src.dispatch.database import get_session
from src.dispatch.exceptions import BadRequestError
from src.dispatch.user.models import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


class VerifyTokenRequest(BaseModel):
    token: str


@router.post("/verify-token", response_model=UserRead)
def verify_token(
    body: VerifyTokenRequest,
    db_session: Session = Depends(get_session),
):
    """Verify Firebase ID token and return/create user."""
    try:
        decoded = auth_service.verify_firebase_token(body.token)
    except ValueError as e:
        raise BadRequestError(str(e)) from e

    user = auth_service.get_or_create_user(
        db_session=db_session,
        firebase_uid=decoded["uid"],
        email=decoded.get("email", ""),
        display_name=decoded.get("name"),
    )

    has_profile = user.profile is not None

    return UserRead(
        id=user.id,
        firebase_uid=user.firebase_uid,
        email=user.email,
        display_name=user.display_name,
        created_at=user.created_at,
        has_profile=has_profile,
    )
