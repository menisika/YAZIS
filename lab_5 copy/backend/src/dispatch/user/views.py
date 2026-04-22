from fastapi import APIRouter

from src.dispatch.auth.permissions import CurrentUser
from src.dispatch.database import SessionDep
from src.dispatch.exceptions import NotFoundError
from src.dispatch.user import service as user_service
from src.dispatch.user.models import (
    UserProfileCreate,
    UserProfileRead,
    UserProfileUpdate,
    UserRead,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_current_user(current_user: CurrentUser):
    has_profile = current_user.profile is not None
    return UserRead(
        id=current_user.id,
        firebase_uid=current_user.firebase_uid,
        email=current_user.email,
        display_name=current_user.display_name,
        created_at=current_user.created_at,
        has_profile=has_profile,
    )


@router.get("/me/profile", response_model=UserProfileRead)
def get_profile(current_user: CurrentUser, db_session: SessionDep):
    profile = user_service.get_profile(db_session=db_session, user_id=current_user.id)
    if not profile:
        raise NotFoundError("Profile not found. Complete onboarding first.")
    return profile


@router.post("/me/profile", response_model=UserProfileRead)
def create_profile(
    body: UserProfileCreate,
    current_user: CurrentUser,
    db_session: SessionDep,
):
    return user_service.create_profile(
        db_session=db_session,
        user_id=current_user.id,
        profile_in=body,
    )


@router.patch("/me/profile", response_model=UserProfileRead)
def update_profile(
    body: UserProfileUpdate,
    current_user: CurrentUser,
    db_session: SessionDep,
):
    return user_service.update_profile(
        db_session=db_session,
        user_id=current_user.id,
        profile_in=body,
    )
