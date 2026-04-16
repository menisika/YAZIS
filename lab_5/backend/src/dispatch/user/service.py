from datetime import datetime

from sqlmodel import Session, select

from src.dispatch.common.utils import calculate_bmr, calculate_tdee
from src.dispatch.exceptions import NotFoundError
from src.dispatch.user.models import (
    User,
    UserProfile,
    UserProfileCreate,
    UserProfileUpdate,
)


def get(*, db_session: Session, user_id: int) -> User:
    user = db_session.get(User, user_id)
    if not user:
        raise NotFoundError("User not found")
    return user


def get_profile(*, db_session: Session, user_id: int) -> UserProfile | None:
    statement = select(UserProfile).where(UserProfile.user_id == user_id)
    return db_session.exec(statement).first()


def create_profile(*, db_session: Session, user_id: int, profile_in: UserProfileCreate) -> UserProfile:
    bmr = calculate_bmr(
        weight_kg=profile_in.weight_kg,
        height_cm=profile_in.height_cm,
        age=profile_in.age,
        gender=profile_in.gender,
    )
    tdee = calculate_tdee(bmr)

    profile = UserProfile(
        user_id=user_id,
        bmr=bmr,
        tdee=tdee,
        **profile_in.model_dump(),
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile


def update_profile(*, db_session: Session, user_id: int, profile_in: UserProfileUpdate) -> UserProfile:
    profile = get_profile(db_session=db_session, user_id=user_id)
    if not profile:
        raise NotFoundError("Profile not found. Complete onboarding first.")

    update_data = profile_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    # Recalculate BMR/TDEE if relevant fields changed
    if any(k in update_data for k in ("weight_kg", "height_cm", "age", "gender")):
        profile.bmr = calculate_bmr(
            weight_kg=profile.weight_kg,
            height_cm=profile.height_cm,
            age=profile.age,
            gender=profile.gender,
        )
        profile.tdee = calculate_tdee(profile.bmr)

    profile.updated_at = datetime.utcnow()
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile
