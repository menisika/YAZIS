from datetime import date, datetime

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

# --- SQLModel Tables ---


class WorkoutPlan(SQLModel, table=True):
    __tablename__ = "workout_plan"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    name: str = ""
    plan_type: str = "generated"  # generated / custom
    created_at: datetime = Field(default_factory=datetime.utcnow)
    valid_from: date | None = None
    valid_to: date | None = None

    days: list["WorkoutPlanDay"] = Relationship(back_populates="plan")


class WorkoutPlanDay(SQLModel, table=True):
    __tablename__ = "workout_plan_day"

    id: int | None = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="workout_plan.id", index=True)
    day_of_week: int  # 0=Monday .. 6=Sunday
    focus: str = ""  # Push, Pull, Legs, Upper, Lower, Full Body, Rest
    order_index: int = 0

    plan: WorkoutPlan | None = Relationship(back_populates="days")
    exercises: list["WorkoutPlanExercise"] = Relationship(back_populates="plan_day")


class WorkoutPlanExercise(SQLModel, table=True):
    __tablename__ = "workout_plan_exercise"

    id: int | None = Field(default=None, primary_key=True)
    plan_day_id: int = Field(foreign_key="workout_plan_day.id", index=True)
    exercise_id: int = Field(foreign_key="exercise.id")
    sets: int = 3
    reps_min: int = 8
    reps_max: int = 12
    rest_seconds: int = 90
    order_index: int = 0
    notes: str | None = None

    plan_day: WorkoutPlanDay | None = Relationship(back_populates="exercises")


# --- Pydantic Schemas ---


class WorkoutPlanExerciseRead(BaseModel):
    id: int
    exercise_id: int
    exercise_name: str | None = None
    sets: int
    reps_min: int
    reps_max: int
    rest_seconds: int
    order_index: int
    notes: str | None


class WorkoutPlanDayRead(BaseModel):
    id: int
    day_of_week: int
    focus: str
    order_index: int
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
