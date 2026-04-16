from fastapi import APIRouter, Query

from src.dispatch.analytics import service as analytics_service
from src.dispatch.analytics.models import (
    AnalyticsSummary,
    CalorieEntry,
    ExerciseProgression,
    MuscleDistribution,
    WeeklyFrequency,
)
from src.dispatch.auth.permissions import CurrentUser
from src.dispatch.database import SessionDep

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(
    current_user: CurrentUser,
    db_session: SessionDep,
    period: int = Query(default=30, description="Period in days"),
):
    return analytics_service.get_summary(
        db_session=db_session, user_id=current_user.id, period_days=period
    )


@router.get("/frequency", response_model=list[WeeklyFrequency])
def get_frequency(
    current_user: CurrentUser,
    db_session: SessionDep,
    weeks: int = Query(default=12, ge=1, le=52),
):
    return analytics_service.get_frequency(
        db_session=db_session, user_id=current_user.id, weeks=weeks
    )


@router.get("/muscle-distribution", response_model=list[MuscleDistribution])
def get_muscle_distribution(
    current_user: CurrentUser,
    db_session: SessionDep,
    period: int = Query(default=30),
):
    return analytics_service.get_muscle_distribution(
        db_session=db_session, user_id=current_user.id, period_days=period
    )


@router.get("/progression", response_model=list[ExerciseProgression])
def get_progression(
    current_user: CurrentUser,
    db_session: SessionDep,
    exercise_id: int = Query(...),
    period: int = Query(default=90),
):
    return analytics_service.get_progression(
        db_session=db_session,
        user_id=current_user.id,
        exercise_id=exercise_id,
        period_days=period,
    )


@router.get("/calories", response_model=list[CalorieEntry])
def get_calories(
    current_user: CurrentUser,
    db_session: SessionDep,
    period: int = Query(default=30),
):
    return analytics_service.get_calories(
        db_session=db_session, user_id=current_user.id, period_days=period
    )
