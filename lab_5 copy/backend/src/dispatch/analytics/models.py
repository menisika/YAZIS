from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    total_sessions: int = 0
    total_duration_minutes: int = 0
    total_volume_kg: float = 0.0
    total_calories: float = 0.0
    current_streak: int = 0
    sessions_this_week: int = 0


class WeeklyFrequency(BaseModel):
    week: str  # ISO week string e.g. "2026-W15"
    count: int


class MuscleDistribution(BaseModel):
    muscle_group: str
    total_sets: int
    total_volume_kg: float


class ExerciseProgression(BaseModel):
    date: str
    max_weight_kg: float
    total_volume_kg: float
    total_reps: int


class CalorieEntry(BaseModel):
    date: str
    calories: float
