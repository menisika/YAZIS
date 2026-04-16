from math import ceil

from pydantic import BaseModel


class PaginationParams(BaseModel):
    offset: int = 0
    limit: int = 20


class PaginatedResponse(BaseModel):
    items: list
    total: int
    offset: int
    limit: int
    pages: int

    @classmethod
    def create(cls, items: list, total: int, offset: int, limit: int):
        return cls(
            items=items,
            total=total,
            offset=offset,
            limit=limit,
            pages=ceil(total / limit) if limit > 0 else 0,
        )


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Mifflin-St Jeor equation for BMR."""
    if gender == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def calculate_tdee(bmr: float, activity_multiplier: float = 1.55) -> float:
    """Total Daily Energy Expenditure. Default multiplier for moderate activity."""
    return bmr * activity_multiplier


def estimate_calories_burned(
    met_value: float, weight_kg: float, duration_minutes: float
) -> float:
    """Estimate calories burned for an exercise."""
    return met_value * weight_kg * (duration_minutes / 60)
