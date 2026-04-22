from datetime import datetime

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

# --- SQLModel Tables ---


class WorkoutSession(SQLModel, table=True):
    __tablename__ = "workout_session"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    plan_id: int | None = None
    plan_day_of_week: int | None = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None
    duration_seconds: int | None = None
    status: str = "in_progress"  # in_progress / completed / abandoned
    estimated_calories: float | None = None
    notes: str | None = None

    sets: list["SessionSet"] = Relationship(back_populates="session")


class SessionSet(SQLModel, table=True):
    __tablename__ = "session_set"

    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="workout_session.id", index=True)
    exercise_id: int = Field(foreign_key="exercise.id")
    set_number: int = 1
    weight_kg: float | None = None
    reps: int = 0
    duration_seconds: int | None = None
    rpe: int | None = None  # Rate of Perceived Exertion 1-10
    completed_at: datetime = Field(default_factory=datetime.utcnow)

    session: WorkoutSession | None = Relationship(back_populates="sets")


# --- Pydantic Schemas ---


class SessionSetCreate(BaseModel):
    exercise_id: int
    set_number: int
    weight_kg: float | None = None
    reps: int = 0
    duration_seconds: int | None = None
    rpe: int | None = None


class SessionSetRead(BaseModel):
    id: int
    exercise_id: int
    exercise_name: str | None = None
    set_number: int
    weight_kg: float | None
    reps: int
    duration_seconds: int | None
    rpe: int | None
    completed_at: datetime


class SessionCreate(BaseModel):
    plan_id: int | None = None
    plan_day_of_week: int | None = None
    notes: str | None = None


class SessionUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None


class SessionRead(BaseModel):
    id: int
    user_id: int
    plan_id: int | None
    plan_day_of_week: int | None
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: int | None
    status: str
    estimated_calories: float | None
    notes: str | None
    sets: list[SessionSetRead] = []
