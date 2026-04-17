from pydantic import BaseModel
from sqlmodel import Field, SQLModel

# --- SQLModel Tables ---


class Exercise(SQLModel, table=True):
    __tablename__ = "exercise"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str = ""
    category: str  # strength, cardio, stretching, plyometrics
    equipment: str  # barbell, dumbbell, bodyweight, machine, cable, band
    difficulty: str  # beginner, intermediate, advanced
    instructions: str = ""
    met_value: float = 3.5
    youtube_video_id: str | None = None
    slug: str | None = Field(default=None, unique=True, index=True)


class ExerciseMuscleGroup(SQLModel, table=True):
    __tablename__ = "exercise_muscle_group"

    exercise_id: int = Field(foreign_key="exercise.id", primary_key=True)
    muscle_group: str = Field(primary_key=True)
    is_primary: bool = True


# --- Pydantic Schemas ---


class ExerciseRead(BaseModel):
    id: int
    name: str
    description: str
    category: str
    equipment: str
    difficulty: str
    instructions: str
    met_value: float
    youtube_video_id: str | None = None
    muscle_groups: list["MuscleGroupRead"] = []


class MuscleGroupRead(BaseModel):
    muscle_group: str
    is_primary: bool


class ExerciseVideoResponse(BaseModel):
    youtube_video_id: str | None = None


class ExerciseFilter(BaseModel):
    muscle_group: str | None = None
    category: str | None = None
    equipment: str | None = None
    difficulty: str | None = None
    search: str | None = None
