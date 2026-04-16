"""LangGraph agent tools for workout generation."""

import json
from datetime import date, timedelta

from langchain_core.tools import tool
from sqlmodel import Session, func, select

from src.dispatch.exercise.models import Exercise, ExerciseMuscleGroup
from src.dispatch.session.models import SessionSet, WorkoutSession
from src.dispatch.user.models import UserProfile
from src.dispatch.workout import service as workout_service


@tool
def get_user_profile(user_id: int, db_session_json: str) -> str:
    """Get user's biometrics, fitness level, preferences, and injuries.

    Args:
        user_id: The user's ID
        db_session_json: Placeholder — session is injected at runtime
    """
    # This tool is called with injected context, not directly
    return "Tool requires runtime injection"


@tool
def get_exercise_catalog(
    muscle_group: str,
    difficulty: str = "",
    equipment: str = "",
) -> str:
    """Query exercises by muscle group, difficulty, and equipment.

    Args:
        muscle_group: Target muscle group (chest, back, shoulders, biceps, triceps, quadriceps, hamstrings, glutes, calves, abs)
        difficulty: Filter by difficulty level (beginner, intermediate, advanced). Empty string for all.
        equipment: Filter by equipment type (barbell, dumbbell, bodyweight, machine, cable, band). Empty string for all.
    """
    return "Tool requires runtime injection"


@tool
def check_recovery_status(user_id: int) -> str:
    """Analyze last 7 days of sessions and return fatigue scores per muscle group.

    Args:
        user_id: The user's ID
    """
    return "Tool requires runtime injection"


@tool
def get_recent_workout_history(user_id: int, days: int = 14) -> str:
    """Return exercises performed in the last N days for variety tracking.

    Args:
        user_id: The user's ID
        days: Number of days to look back (default 14)
    """
    return "Tool requires runtime injection"


@tool
def save_workout_plan(
    user_id: int,
    plan_name: str,
    week_start: str,
    days_json: str,
) -> str:
    """Save a generated workout plan to the database.

    Args:
        user_id: The user's ID
        plan_name: Name for the plan (e.g. "Week of Apr 14 - Push/Pull/Legs")
        week_start: ISO date string for week start (e.g. "2026-04-13")
        days_json: JSON string of days array. Each day has: day_of_week (0-6), focus (string), exercises (array of {exercise_id, sets, reps_min, reps_max, rest_seconds, order_index, notes})
    """
    return "Tool requires runtime injection"


# --- Runtime tool implementations (called with actual db_session) ---


def create_runtime_tools(db_session: Session, user_id: int):
    """Create tool implementations with injected db_session."""

    @tool
    def get_user_profile_impl() -> str:
        """Get user's biometrics, fitness level, preferences, and injuries."""
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        profile = db_session.exec(stmt).first()
        if not profile:
            return json.dumps({"error": "No profile found"})
        return json.dumps({
            "age": profile.age,
            "gender": profile.gender,
            "height_cm": profile.height_cm,
            "weight_kg": profile.weight_kg,
            "fitness_level": profile.fitness_level,
            "preferred_workout_types": profile.preferred_workout_types,
            "workout_days_per_week": profile.workout_days_per_week,
            "session_duration_min": profile.session_duration_min,
            "injuries": profile.injuries,
            "bmr": profile.bmr,
            "tdee": profile.tdee,
        })

    @tool
    def get_exercise_catalog_impl(
        muscle_group: str,
        difficulty: str = "",
        equipment: str = "",
    ) -> str:
        """Query exercises by muscle group, difficulty, and equipment.

        Args:
            muscle_group: Target muscle group
            difficulty: Optional difficulty filter
            equipment: Optional equipment filter
        """
        stmt = (
            select(Exercise)
            .join(ExerciseMuscleGroup)
            .where(ExerciseMuscleGroup.muscle_group == muscle_group)
            .where(ExerciseMuscleGroup.is_primary == True)
        )
        if difficulty:
            stmt = stmt.where(Exercise.difficulty == difficulty)
        if equipment:
            stmt = stmt.where(Exercise.equipment == equipment)

        exercises = db_session.exec(stmt.limit(30)).all()
        return json.dumps([
            {
                "id": e.id,
                "name": e.name,
                "category": e.category,
                "equipment": e.equipment,
                "difficulty": e.difficulty,
                "met_value": e.met_value,
            }
            for e in exercises
        ])

    @tool
    def check_recovery_status_impl() -> str:
        """Analyze last 7 days of sessions and return fatigue scores per muscle group."""
        seven_days_ago = date.today() - timedelta(days=7)
        stmt = (
            select(
                ExerciseMuscleGroup.muscle_group,
                func.count(SessionSet.id).label("total_sets"),
            )
            .select_from(SessionSet)
            .join(Exercise, SessionSet.exercise_id == Exercise.id)
            .join(ExerciseMuscleGroup, ExerciseMuscleGroup.exercise_id == Exercise.id)
            .join(WorkoutSession, SessionSet.session_id == WorkoutSession.id)
            .where(WorkoutSession.user_id == user_id)
            .where(WorkoutSession.started_at >= seven_days_ago.isoformat())
            .where(ExerciseMuscleGroup.is_primary == True)
            .group_by(ExerciseMuscleGroup.muscle_group)
        )
        results = db_session.exec(stmt).all()

        max_sets = {"beginner": 10, "intermediate": 16, "advanced": 22}
        profile_stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        profile = db_session.exec(profile_stmt).first()
        max_vol = max_sets.get(profile.fitness_level if profile else "intermediate", 16)

        recovery = {}
        for muscle, sets in results:
            fatigue = min(sets / max_vol, 1.0)
            recovery[muscle] = {"sets_last_7d": sets, "fatigue_score": round(fatigue, 2)}

        return json.dumps(recovery)

    @tool
    def get_recent_workout_history_impl(days: int = 14) -> str:
        """Return exercises performed in the last N days.

        Args:
            days: Number of days to look back
        """
        cutoff = date.today() - timedelta(days=days)
        stmt = (
            select(Exercise.id, Exercise.name, func.count(SessionSet.id).label("times_used"))
            .select_from(SessionSet)
            .join(Exercise, SessionSet.exercise_id == Exercise.id)
            .join(WorkoutSession, SessionSet.session_id == WorkoutSession.id)
            .where(WorkoutSession.user_id == user_id)
            .where(WorkoutSession.started_at >= cutoff.isoformat())
            .group_by(Exercise.id, Exercise.name)
        )
        results = db_session.exec(stmt).all()
        return json.dumps([
            {"exercise_id": r[0], "name": r[1], "times_used": r[2]}
            for r in results
        ])

    @tool
    def save_workout_plan_impl(
        plan_name: str,
        week_start: str,
        days_json: str,
    ) -> str:
        """Save generated workout plan to database.

        Args:
            plan_name: Name for the plan
            week_start: ISO date for week start
            days_json: JSON array of day objects with exercises
        """
        start = date.fromisoformat(week_start)
        end = start + timedelta(days=6)
        days_data = json.loads(days_json)

        plan = workout_service.save_generated_plan(
            db_session=db_session,
            user_id=user_id,
            name=plan_name,
            valid_from=start,
            valid_to=end,
            days_data=days_data,
        )
        return json.dumps({"plan_id": plan.id, "name": plan.name, "status": "saved"})

    return [
        get_user_profile_impl,
        get_exercise_catalog_impl,
        check_recovery_status_impl,
        get_recent_workout_history_impl,
        save_workout_plan_impl,
    ]
