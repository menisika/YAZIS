from datetime import date, datetime

from pydantic import BaseModel
from sqlalchemy import ForeignKeyConstraint
from sqlmodel import Field, SQLModel

# --- SQLModel Tables ---


class WorkoutPlan(SQLModel, table=True):
    __tablename__ = "workout_plan"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)
    name: str = ""
    plan_type: str = "generated"  # generated / custom
    created_at: datetime = Field(default_factory=datetime.utcnow)
    valid_from: date | None = None
    valid_to: date | None = None


class WorkoutPlanDay(SQLModel, table=True):
    __tablename__ = "workout_plan_day"

    plan_id: int = Field(foreign_key="workout_plan.id", primary_key=True)
    day_of_week: int = Field(primary_key=True)  # 0=Monday .. 6=Sunday
    focus: str = ""  # Push, Pull, Legs, Upper, Lower, Full Body, Rest
    is_rest: bool = False


class WorkoutPlanExercise(SQLModel, table=True):
    __tablename__ = "workout_plan_exercise"

    id: int | None = Field(default=None, primary_key=True)
    plan_id: int = Field(index=True)
    day_of_week: int = Field(index=True)
    exercise_id: int = Field(foreign_key="exercise.id")
    sets: int = 3
    reps_min: int = 8
    reps_max: int = 12
    rest_seconds: int = 90
    order_index: int = 0
    notes: str | None = None

    __table_args__ = (
        ForeignKeyConstraint(
            ["plan_id", "day_of_week"],
            ["workout_plan_day.plan_id", "workout_plan_day.day_of_week"],
            ondelete="CASCADE",
        ),
    )


# --- Pydantic Schemas ---


class WorkoutPlanExerciseRead(BaseModel):
    id: int
    exercise_id: int
    exercise_name: str | None = None
    exercise_description: str | None = None
    sets: int
    reps_min: int
    reps_max: int
    rest_seconds: int
    order_index: int
    notes: str | None


class WorkoutPlanDayRead(BaseModel):
    plan_id: int
    day_of_week: int
    focus: str
    is_rest: bool
    status: str  # rest | done | today | skipped | upcoming
    exercises: list[WorkoutPlanExerciseRead] = []


class WorkoutPlanRead(BaseModel):
    id: int
    user_id: int
    name: str
    plan_type: str
    created_at: datetime
    valid_from: date | None
    valid_to: date | None
    days: list[WorkoutPlanDayRead] = []


class GenerateWorkoutRequest(BaseModel):
    week_start: date | None = None
    focus_muscle_groups: list[str] | None = None
    exclude_exercises: list[int] | None = None


class SwapDaysRequest(BaseModel):
    day_a: int
    day_b: int
