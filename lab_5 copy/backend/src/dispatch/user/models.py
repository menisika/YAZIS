from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

# --- SQLModel Tables ---


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: int | None = Field(default=None, primary_key=True)
    firebase_uid: str = Field(unique=True, index=True)
    email: str
    display_name: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    profile: Optional["UserProfile"] = Relationship(back_populates="user")


class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profile"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    fitness_level: str = "beginner"
    preferred_workout_types: list[str] = Field(default=[], sa_column=Column(JSON))
    workout_days_per_week: int = 4
    session_duration_min: int = 60
    bmr: float = 0.0
    tdee: float = 0.0
    injuries: list[str] = Field(default=[], sa_column=Column(JSON))
    calorie_goal: int = 500
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="profile")


# --- Pydantic Schemas ---


class UserRead(BaseModel):
    id: int
    firebase_uid: str
    email: str
    display_name: str | None
    created_at: datetime
    has_profile: bool = False


class UserProfileCreate(BaseModel):
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    fitness_level: str = "beginner"
    preferred_workout_types: list[str] = []
    workout_days_per_week: int = 4
    session_duration_min: int = 60
    injuries: list[str] = []
    calorie_goal: int = 500


class UserProfileUpdate(BaseModel):
    age: int | None = None
    gender: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    fitness_level: str | None = None
    preferred_workout_types: list[str] | None = None
    workout_days_per_week: int | None = None
    session_duration_min: int | None = None
    injuries: list[str] | None = None
    calorie_goal: int | None = None


class UserProfileRead(BaseModel):
    id: int
    user_id: int
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    fitness_level: str
    preferred_workout_types: list[str]
    workout_days_per_week: int
    session_duration_min: int
    bmr: float
    tdee: float
    injuries: list[str]
    calorie_goal: int
    updated_at: datetime
