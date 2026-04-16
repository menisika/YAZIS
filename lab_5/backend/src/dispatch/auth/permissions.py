from typing import Annotated

from fastapi import Depends, Request
from sqlmodel import Session

from src.dispatch.auth import service as auth_service
from src.dispatch.database import get_session
from src.dispatch.exceptions import UnauthorizedError
from src.dispatch.user.models import User


async def get_current_user(
    request: Request,
    db_session: Session = Depends(get_session),
) -> User:
    """Extract and verify Firebase token from Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedError("Missing or invalid Authorization header")

    token = auth_header.split("Bearer ")[1]

    try:
        decoded = auth_service.verify_firebase_token(token)
    except ValueError as e:
        raise UnauthorizedError("Invalid or expired token") from e

    user = auth_service.get_or_create_user(
        db_session=db_session,
        firebase_uid=decoded["uid"],
        email=decoded.get("email", ""),
        display_name=decoded.get("name"),
    )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
