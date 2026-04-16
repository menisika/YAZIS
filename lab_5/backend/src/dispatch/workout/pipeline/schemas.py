"""Pydantic schemas for the workout generation pipeline."""

from typing import Any, TypedDict

from pydantic import BaseModel


# ── Architect output ──────────────────────────────────────────────────────────


class PlannedExercise(BaseModel):
    name: str
    sets: int = 3
    reps_min: int = 8
    reps_max: int = 12
    rest_seconds: int = 90
    notes: str = ""


class PlannedDay(BaseModel):
    day_of_week: int  # 0 = Monday … 6 = Sunday
    focus: str  # e.g. "Push", "Pull", "Legs", "Rest"
    is_rest: bool = False
    exercises: list[PlannedExercise] = []


class WeeklyPlanSchema(BaseModel):
    name: str
    plan_type: str = "generated"
    days: list[PlannedDay]  # exactly 7 entries


# ── Librarian output ──────────────────────────────────────────────────────────


class GeneratedExercise(BaseModel):
    name: str
    slug: str
    description: str
    instructions: str
    category: str        # strength | cardio | stretching | plyometrics
    equipment: str       # barbell | dumbbell | bodyweight | machine | cable | band
    difficulty: str      # beginner | intermediate | advanced
    met_value: float
    muscle_groups: list[str]   # all muscle groups involved
    primary_muscles: list[str] # subset that are primary movers


class ExerciseBatchSchema(BaseModel):
    exercises: list[GeneratedExercise]


# ── LangGraph state ───────────────────────────────────────────────────────────


class PipelineState(TypedDict, total=False):
    user_id: int
    week_start: str
    preferences: dict
    user_profile_json: str
    existing_names: list[str]
    weekly_plan: Any          # WeeklyPlanSchema instance after Architect
    exercise_map: Any         # dict[slug, Exercise] after Librarian
    result: Any               # WorkoutPlanRead after Persist
