"""Orchestrates workout generation flow."""

import json
from datetime import date

from sqlmodel import Session, select

from src.dispatch.exercise import service as exercise_service
from src.dispatch.user.models import UserProfile
from src.dispatch.workout.pipeline.graph import build_pipeline


async def generate_plan_flow(
    *,
    db_session: Session,
    user_id: int,
    week_start: date | None = None,
    focus_muscle_groups: list[str] | None = None,
    exclude_exercises: list[int] | None = None,
) -> dict:
    """Full flow: run the LangGraph pipeline to generate and save a workout plan."""
    if week_start is None:
        today = date.today()
        week_start = today - __import__("datetime").timedelta(days=today.weekday())

    preferences: dict = {}
    if focus_muscle_groups:
        preferences["focus_muscle_groups"] = focus_muscle_groups
    if exclude_exercises:
        preferences["exclude_exercises"] = exclude_exercises

    # Fetch user profile for Architect context
    profile = db_session.exec(
        select(UserProfile).where(UserProfile.user_id == user_id)
    ).first()
    user_profile_json = json.dumps(
        {
            "age": profile.age if profile else None,
            "gender": profile.gender if profile else None,
            "height_cm": profile.height_cm if profile else None,
            "weight_kg": profile.weight_kg if profile else None,
            "fitness_level": profile.fitness_level if profile else "beginner",
            "preferred_workout_types": profile.preferred_workout_types if profile else [],
            "workout_days_per_week": profile.workout_days_per_week if profile else 4,
            "session_duration_min": profile.session_duration_min if profile else 60,
            "injuries": profile.injuries if profile else [],
        }
    )

    # Fetch existing exercise names for Architect dedup pass
    existing_names = exercise_service.get_all_names(db_session=db_session)

    initial_state = {
        "user_id": user_id,
        "week_start": week_start.isoformat(),
        "preferences": preferences,
        "user_profile_json": user_profile_json,
        "existing_names": existing_names,
    }

    pipeline = build_pipeline(db_session=db_session)
    final_state = pipeline.invoke(initial_state)

    result = final_state.get("result")
    return {
        "plan": result.model_dump() if result else None,
        "week_start": week_start.isoformat(),
    }
