from datetime import date, timedelta

from sqlmodel import Session, func, select, text

from src.dispatch.analytics.models import (
    AnalyticsSummary,
    CalorieEntry,
    ExerciseProgression,
    MuscleDistribution,
    WeeklyFrequency,
)
from src.dispatch.exercise.models import ExerciseMuscleGroup
from src.dispatch.session.models import SessionSet, WorkoutSession


def get_summary(*, db_session: Session, user_id: int, period_days: int = 30) -> AnalyticsSummary:
    cutoff = date.today() - timedelta(days=period_days)

    stmt = (
        select(
            func.count(WorkoutSession.id),
            func.coalesce(func.sum(WorkoutSession.duration_seconds), 0),
            func.coalesce(func.sum(WorkoutSession.estimated_calories), 0),
        )
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.started_at >= cutoff.isoformat())
    )
    result = db_session.exec(stmt).first()
    total_sessions, total_duration, total_calories = result or (0, 0, 0)

    # Total volume
    vol_stmt = (
        select(func.coalesce(func.sum(SessionSet.weight_kg * SessionSet.reps), 0))
        .select_from(SessionSet)
        .join(WorkoutSession, SessionSet.session_id == WorkoutSession.id)
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.started_at >= cutoff.isoformat())
    )
    total_volume = db_session.exec(vol_stmt).first() or 0

    # This week sessions
    week_start = date.today() - timedelta(days=date.today().weekday())
    week_stmt = (
        select(func.count(WorkoutSession.id))
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.started_at >= week_start.isoformat())
    )
    sessions_this_week = db_session.exec(week_stmt).first() or 0

    return AnalyticsSummary(
        total_sessions=total_sessions,
        total_duration_minutes=int(total_duration / 60),
        total_volume_kg=float(total_volume),
        total_calories=float(total_calories),
        current_streak=0,
        sessions_this_week=sessions_this_week,
    )


def get_frequency(*, db_session: Session, user_id: int, weeks: int = 12) -> list[WeeklyFrequency]:
    cutoff = date.today() - timedelta(weeks=weeks)
    stmt = text("""
        SELECT to_char(started_at, 'IYYY-"W"IW') as week, COUNT(*) as count
        FROM workout_session
        WHERE user_id = :user_id AND status = 'completed' AND started_at >= :cutoff
        GROUP BY week ORDER BY week
    """)
    results = db_session.exec(stmt, params={"user_id": user_id, "cutoff": cutoff.isoformat()}).all()
    return [WeeklyFrequency(week=r[0], count=r[1]) for r in results]


def get_muscle_distribution(*, db_session: Session, user_id: int, period_days: int = 30) -> list[MuscleDistribution]:
    cutoff = date.today() - timedelta(days=period_days)
    stmt = (
        select(
            ExerciseMuscleGroup.muscle_group,
            func.count(SessionSet.id).label("total_sets"),
            func.coalesce(func.sum(SessionSet.weight_kg * SessionSet.reps), 0).label("total_volume"),
        )
        .select_from(SessionSet)
        .join(ExerciseMuscleGroup, ExerciseMuscleGroup.exercise_id == SessionSet.exercise_id)
        .join(WorkoutSession, SessionSet.session_id == WorkoutSession.id)
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.status == "completed")
        .where(WorkoutSession.started_at >= cutoff.isoformat())
        .where(ExerciseMuscleGroup.is_primary == True)
        .group_by(ExerciseMuscleGroup.muscle_group)
    )
    results = db_session.exec(stmt).all()
    return [MuscleDistribution(muscle_group=r[0], total_sets=r[1], total_volume_kg=float(r[2])) for r in results]


def get_progression(*, db_session: Session, user_id: int, exercise_id: int, period_days: int = 90) -> list[ExerciseProgression]:
    cutoff = date.today() - timedelta(days=period_days)
    stmt = text("""
        SELECT DATE(ss.completed_at) as d,
               MAX(ss.weight_kg) as max_weight,
               COALESCE(SUM(ss.weight_kg * ss.reps), 0) as total_volume,
               SUM(ss.reps) as total_reps
        FROM session_set ss
        JOIN workout_session ws ON ss.session_id = ws.id
        WHERE ws.user_id = :user_id AND ss.exercise_id = :exercise_id
          AND ws.started_at >= :cutoff AND ws.status = 'completed'
        GROUP BY d ORDER BY d
    """)
    results = db_session.exec(stmt, params={
        "user_id": user_id, "exercise_id": exercise_id, "cutoff": cutoff.isoformat()
    }).all()
    return [ExerciseProgression(date=str(r[0]), max_weight_kg=float(r[1] or 0), total_volume_kg=float(r[2]), total_reps=int(r[3] or 0)) for r in results]


def get_calories(*, db_session: Session, user_id: int, period_days: int = 30) -> list[CalorieEntry]:
    cutoff = date.today() - timedelta(days=period_days)
    stmt = text("""
        SELECT DATE(started_at) as d, SUM(estimated_calories) as cals
        FROM workout_session
        WHERE user_id = :user_id AND status = 'completed' AND started_at >= :cutoff
        GROUP BY d ORDER BY d
    """)
    results = db_session.exec(stmt, params={"user_id": user_id, "cutoff": cutoff.isoformat()}).all()
    return [CalorieEntry(date=str(r[0]), calories=float(r[1] or 0)) for r in results]
