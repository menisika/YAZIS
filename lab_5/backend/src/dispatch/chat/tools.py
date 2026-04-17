"""LangGraph agent tools for AI fitness assistant."""

import json

from langchain_core.tools import tool
from sqlmodel import Session, select

from src.dispatch.exercise.models import Exercise, ExerciseMuscleGroup
from src.dispatch.session.models import SessionSet, WorkoutSession
from src.dispatch.user.models import UserProfile
from src.dispatch.workout.models import WorkoutPlan, WorkoutPlanDay, WorkoutPlanExercise


def create_assistant_tools(db_session: Session, user_id: int):
    """Create tool implementations with injected db_session for the AI assistant."""

    @tool
    def get_user_profile() -> str:
        """Get the user's biometrics, fitness level, preferences, and goals."""
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
    def get_current_workout_plan() -> str:
        """Get the user's current week workout plan with all exercises."""
        plan = db_session.exec(
            select(WorkoutPlan).where(WorkoutPlan.user_id == user_id)
        ).first()
        if not plan:
            return json.dumps({"error": "No active plan found"})

        days_stmt = select(WorkoutPlanDay).where(WorkoutPlanDay.plan_id == plan.id).order_by(WorkoutPlanDay.day_of_week)
        days = db_session.exec(days_stmt).all()

        plan_data = {"name": plan.name, "days": []}
        for day in days:
            ex_stmt = (
                select(WorkoutPlanExercise)
                .where(WorkoutPlanExercise.plan_id == day.plan_id)
                .where(WorkoutPlanExercise.day_of_week == day.day_of_week)
                .order_by(WorkoutPlanExercise.order_index)
            )
            exercises = db_session.exec(ex_stmt).all()
            day_data = {
                "day_of_week": day.day_of_week,
                "focus": day.focus,
                "exercises": [],
            }
            for ex in exercises:
                exercise = db_session.get(Exercise, ex.exercise_id)
                day_data["exercises"].append({
                    "name": exercise.name if exercise else "Unknown",
                    "sets": ex.sets,
                    "reps": f"{ex.reps_min}-{ex.reps_max}",
                    "rest_seconds": ex.rest_seconds,
                })
            plan_data["days"].append(day_data)

        return json.dumps(plan_data)

    @tool
    def get_recent_sessions(count: int = 5) -> str:
        """Get the user's most recent workout sessions with details.

        Args:
            count: Number of recent sessions to return
        """
        stmt = (
            select(WorkoutSession)
            .where(WorkoutSession.user_id == user_id)
            .where(WorkoutSession.status == "completed")
            .order_by(WorkoutSession.started_at.desc())
            .limit(count)
        )
        sessions = db_session.exec(stmt).all()

        sessions_data = []
        for s in sessions:
            sets_stmt = select(SessionSet).where(SessionSet.session_id == s.id)
            sets = db_session.exec(sets_stmt).all()
            exercises_done = {}
            for st in sets:
                exercise = db_session.get(Exercise, st.exercise_id)
                name = exercise.name if exercise else "Unknown"
                if name not in exercises_done:
                    exercises_done[name] = {"sets": 0, "max_weight": 0, "total_reps": 0}
                exercises_done[name]["sets"] += 1
                exercises_done[name]["max_weight"] = max(exercises_done[name]["max_weight"], st.weight_kg or 0)
                exercises_done[name]["total_reps"] += st.reps

            sessions_data.append({
                "date": s.started_at.isoformat(),
                "duration_minutes": (s.duration_seconds or 0) // 60,
                "calories": s.estimated_calories,
                "exercises": exercises_done,
            })

        return json.dumps(sessions_data)

    @tool
    def search_exercises(query: str, muscle_group: str = "") -> str:
        """Search exercises by name or filter by muscle group.

        Args:
            query: Search term for exercise name
            muscle_group: Optional muscle group filter
        """
        stmt = select(Exercise).where(Exercise.name.ilike(f"%{query}%"))
        if muscle_group:
            stmt = stmt.join(ExerciseMuscleGroup).where(ExerciseMuscleGroup.muscle_group == muscle_group)
        exercises = db_session.exec(stmt.limit(10)).all()
        return json.dumps([
            {"id": e.id, "name": e.name, "category": e.category, "equipment": e.equipment, "instructions": e.instructions[:200]}
            for e in exercises
        ])

    @tool
    def get_nutrition_info() -> str:
        """Get basic nutrition recommendations based on user profile and goals."""
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        profile = db_session.exec(stmt).first()
        if not profile:
            return json.dumps({"error": "No profile found"})

        # Basic macros based on TDEE
        protein_g = round(profile.weight_kg * 1.8, 0)  # 1.8g/kg for active people
        fat_g = round(profile.tdee * 0.25 / 9, 0)  # 25% from fat
        carb_g = round((profile.tdee - protein_g * 4 - fat_g * 9) / 4, 0)

        return json.dumps({
            "daily_calories": round(profile.tdee),
            "protein_g": protein_g,
            "fat_g": fat_g,
            "carbs_g": carb_g,
            "protein_per_kg": 1.8,
            "notes": "These are estimates. Adjust based on goals: surplus for muscle gain, deficit for fat loss.",
        })

    return [
        get_user_profile,
        get_current_workout_plan,
        get_recent_sessions,
        search_exercises,
        get_nutrition_info,
    ]
