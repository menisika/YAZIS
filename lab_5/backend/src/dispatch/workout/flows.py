"""Orchestrates workout generation flow."""

from datetime import date

from sqlmodel import Session

from src.dispatch.workout.agent import generate_workout_plan


async def generate_plan_flow(
    *,
    db_session: Session,
    user_id: int,
    week_start: date | None = None,
    focus_muscle_groups: list[str] | None = None,
    exclude_exercises: list[int] | None = None,
) -> dict:
    """Full flow: run the LangGraph agent to generate and save a workout plan."""
    if week_start is None:
        # Default to next Monday
        today = date.today()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        week_start = today + __import__("datetime").timedelta(days=days_until_monday)

    preferences = {}
    if focus_muscle_groups:
        preferences["focus_muscle_groups"] = focus_muscle_groups
    if exclude_exercises:
        preferences["exclude_exercises"] = exclude_exercises

    summary = await generate_workout_plan(
        db_session=db_session,
        user_id=user_id,
        week_start=week_start.isoformat(),
        preferences=preferences or None,
    )

    return {"summary": summary, "week_start": week_start.isoformat()}
