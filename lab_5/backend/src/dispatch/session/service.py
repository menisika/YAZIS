from datetime import date, datetime

from sqlmodel import Session, select

from src.dispatch.common.utils import estimate_calories_burned
from src.dispatch.exceptions import BadRequestError, NotFoundError
from src.dispatch.exercise.models import Exercise
from src.dispatch.session.models import (
    SessionCreate,
    SessionSet,
    SessionSetCreate,
    SessionUpdate,
    WorkoutSession,
)
from src.dispatch.user.models import UserProfile


def create(*, db_session: Session, user_id: int, session_in: SessionCreate) -> WorkoutSession:
    if session_in.plan_day_of_week is not None:
        today_dow = date.today().weekday()
        if session_in.plan_day_of_week != today_dow:
            raise BadRequestError("Can only start today's workout")

    workout_session = WorkoutSession(
        user_id=user_id,
        plan_id=session_in.plan_id,
        plan_day_of_week=session_in.plan_day_of_week,
        notes=session_in.notes,
    )
    db_session.add(workout_session)
    db_session.commit()
    db_session.refresh(workout_session)
    return workout_session


def get(*, db_session: Session, session_id: int) -> WorkoutSession | None:
    return db_session.get(WorkoutSession, session_id)


def get_all(*, db_session: Session, user_id: int, offset: int = 0, limit: int = 20) -> list[WorkoutSession]:
    statement = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id)
        .order_by(WorkoutSession.started_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(db_session.exec(statement).all())


def update(*, db_session: Session, session_id: int, user_id: int, session_in: SessionUpdate) -> WorkoutSession:
    workout_session = get(db_session=db_session, session_id=session_id)
    if not workout_session or workout_session.user_id != user_id:
        raise NotFoundError("Session not found")

    if session_in.status:
        workout_session.status = session_in.status
        if session_in.status in ("completed", "abandoned"):
            workout_session.ended_at = datetime.utcnow()
            if workout_session.started_at:
                delta = workout_session.ended_at - workout_session.started_at
                workout_session.duration_seconds = int(delta.total_seconds())
            # Calculate calories
            workout_session.estimated_calories = _calculate_session_calories(
                db_session=db_session, session=workout_session
            )

    if session_in.notes is not None:
        workout_session.notes = session_in.notes

    db_session.add(workout_session)
    db_session.commit()
    db_session.refresh(workout_session)
    return workout_session


def log_set(*, db_session: Session, session_id: int, user_id: int, set_in: SessionSetCreate) -> SessionSet:
    workout_session = get(db_session=db_session, session_id=session_id)
    if not workout_session or workout_session.user_id != user_id:
        raise NotFoundError("Session not found")

    session_set = SessionSet(
        session_id=session_id,
        **set_in.model_dump(),
    )
    db_session.add(session_set)
    db_session.commit()
    db_session.refresh(session_set)
    return session_set


def delete_set(*, db_session: Session, session_id: int, set_id: int, user_id: int) -> bool:
    workout_session = get(db_session=db_session, session_id=session_id)
    if not workout_session or workout_session.user_id != user_id:
        raise NotFoundError("Session not found")

    session_set = db_session.get(SessionSet, set_id)
    if not session_set or session_set.session_id != session_id:
        raise NotFoundError("Set not found")

    db_session.delete(session_set)
    db_session.commit()
    return True


def _calculate_session_calories(*, db_session: Session, session: WorkoutSession) -> float:
    profile_stmt = select(UserProfile).where(UserProfile.user_id == session.user_id)
    profile = db_session.exec(profile_stmt).first()
    if not profile:
        return 0.0

    sets_stmt = select(SessionSet).where(SessionSet.session_id == session.id)
    sets = db_session.exec(sets_stmt).all()

    total_calories = 0.0
    for s in sets:
        exercise = db_session.get(Exercise, s.exercise_id)
        if exercise:
            # Estimate ~3 seconds per rep
            duration_min = (s.reps * 3) / 60 if s.reps else (s.duration_seconds or 0) / 60
            total_calories += estimate_calories_burned(
                met_value=exercise.met_value,
                weight_kg=profile.weight_kg,
                duration_minutes=duration_min,
            )

    return round(total_calories, 1)
