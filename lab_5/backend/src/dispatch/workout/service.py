from datetime import date

from sqlalchemy import text
from sqlmodel import Session, select

from src.dispatch.exceptions import NotFoundError
from src.dispatch.exercise.models import Exercise
from src.dispatch.workout.models import (
    WorkoutPlan,
    WorkoutPlanDay,
    WorkoutPlanExercise,
    WorkoutPlanDayRead,
    WorkoutPlanExerciseRead,
    WorkoutPlanRead,
)


def get(*, db_session: Session, plan_id: int) -> WorkoutPlan | None:
    return db_session.get(WorkoutPlan, plan_id)


def get_user_plan(*, db_session: Session, user_id: int) -> WorkoutPlan | None:
    return db_session.exec(
        select(WorkoutPlan).where(WorkoutPlan.user_id == user_id)
    ).first()


def get_all(*, db_session: Session, user_id: int) -> list[WorkoutPlan]:
    statement = select(WorkoutPlan).where(WorkoutPlan.user_id == user_id).order_by(WorkoutPlan.created_at.desc())
    return list(db_session.exec(statement).all())


def get_plan_read(*, db_session: Session, plan_id: int) -> WorkoutPlanRead | None:
    plan = get(db_session=db_session, plan_id=plan_id)
    if not plan:
        return None
    return _to_plan_read(db_session=db_session, plan=plan)


def get_today_plan(*, db_session: Session, user_id: int) -> WorkoutPlanDayRead | None:
    plan = get_user_plan(db_session=db_session, user_id=user_id)
    if not plan:
        return None

    day_of_week = date.today().weekday()
    plan_day = db_session.exec(
        select(WorkoutPlanDay)
        .where(WorkoutPlanDay.plan_id == plan.id)
        .where(WorkoutPlanDay.day_of_week == day_of_week)
    ).first()
    if not plan_day:
        return None

    return _to_day_read(db_session=db_session, day=plan_day)


def delete_user_plan(*, db_session: Session, user_id: int) -> None:
    """Delete the user's active plan. Cascade handles days and exercises."""
    plan = get_user_plan(db_session=db_session, user_id=user_id)
    if plan:
        db_session.delete(plan)
        db_session.commit()


def delete(*, db_session: Session, plan_id: int, user_id: int) -> bool:
    plan = get(db_session=db_session, plan_id=plan_id)
    if not plan or plan.user_id != user_id:
        raise NotFoundError("Workout plan not found")
    db_session.delete(plan)
    db_session.commit()
    return True


def save_generated_plan(
    *,
    db_session: Session,
    user_id: int,
    name: str,
    valid_from: date,
    valid_to: date,
    days_data: list[dict],
) -> WorkoutPlan:
    plan = WorkoutPlan(
        user_id=user_id,
        name=name,
        plan_type="generated",
        valid_from=valid_from,
        valid_to=valid_to,
    )
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)

    for day_data in days_data:
        dow = day_data["day_of_week"]
        day = WorkoutPlanDay(
            plan_id=plan.id,
            day_of_week=dow,
            focus=day_data["focus"],
            is_rest=day_data.get("is_rest", False),
        )
        db_session.add(day)
        db_session.commit()

        for ex_idx, ex_data in enumerate(day_data.get("exercises", [])):
            exercise = WorkoutPlanExercise(
                plan_id=plan.id,
                day_of_week=dow,
                exercise_id=ex_data["exercise_id"],
                sets=ex_data.get("sets", 3),
                reps_min=ex_data.get("reps_min", 8),
                reps_max=ex_data.get("reps_max", 12),
                rest_seconds=ex_data.get("rest_seconds", 90),
                order_index=ex_data.get("order_index", ex_idx),
                notes=ex_data.get("notes"),
            )
            db_session.add(exercise)

    db_session.commit()
    db_session.refresh(plan)
    return plan


def swap_days(*, db_session: Session, plan_id: int, day_a: int, day_b: int) -> None:
    if day_a == day_b:
        return

    day_a_row = db_session.exec(
        select(WorkoutPlanDay)
        .where(WorkoutPlanDay.plan_id == plan_id)
        .where(WorkoutPlanDay.day_of_week == day_a)
    ).first()
    day_b_row = db_session.exec(
        select(WorkoutPlanDay)
        .where(WorkoutPlanDay.plan_id == plan_id)
        .where(WorkoutPlanDay.day_of_week == day_b)
    ).first()
    if not day_a_row or not day_b_row:
        raise NotFoundError("Day not found")

    # Move exercises atomically; both target days exist so no FK violation
    db_session.execute(
        text("""
            UPDATE workout_plan_exercise
            SET day_of_week = CASE WHEN day_of_week = :day_a THEN :day_b ELSE :day_a END
            WHERE plan_id = :plan_id AND day_of_week IN (:day_a, :day_b)
        """),
        {"plan_id": plan_id, "day_a": day_a, "day_b": day_b},
    )

    day_a_focus, day_a_is_rest = day_a_row.focus, day_a_row.is_rest
    day_a_row.focus = day_b_row.focus
    day_a_row.is_rest = day_b_row.is_rest
    day_b_row.focus = day_a_focus
    day_b_row.is_rest = day_a_is_rest
    db_session.add(day_a_row)
    db_session.add(day_b_row)
    db_session.commit()


def toggle_rest(*, db_session: Session, plan_id: int, day_of_week: int) -> None:
    day = db_session.exec(
        select(WorkoutPlanDay)
        .where(WorkoutPlanDay.plan_id == plan_id)
        .where(WorkoutPlanDay.day_of_week == day_of_week)
    ).first()
    if not day:
        raise NotFoundError("Day not found")

    day.is_rest = not day.is_rest
    if day.is_rest:
        day.focus = "Rest"
        db_session.execute(
            text("DELETE FROM workout_plan_exercise WHERE plan_id = :plan_id AND day_of_week = :dow"),
            {"plan_id": plan_id, "dow": day_of_week},
        )
    else:
        day.focus = "Training"
    db_session.add(day)
    db_session.commit()


def _to_plan_read(*, db_session: Session, plan: WorkoutPlan) -> WorkoutPlanRead:
    days = db_session.exec(
        select(WorkoutPlanDay)
        .where(WorkoutPlanDay.plan_id == plan.id)
        .order_by(WorkoutPlanDay.day_of_week)
    ).all()
    return WorkoutPlanRead(
        **plan.model_dump(),
        days=[_to_day_read(db_session=db_session, day=d) for d in days],
    )


def _to_day_read(*, db_session: Session, day: WorkoutPlanDay) -> WorkoutPlanDayRead:
    exercises = db_session.exec(
        select(WorkoutPlanExercise)
        .where(WorkoutPlanExercise.plan_id == day.plan_id)
        .where(WorkoutPlanExercise.day_of_week == day.day_of_week)
        .order_by(WorkoutPlanExercise.order_index)
    ).all()
    ex_reads = []
    for ex in exercises:
        exercise = db_session.get(Exercise, ex.exercise_id)
        ex_reads.append(WorkoutPlanExerciseRead(
            id=ex.id,
            exercise_id=ex.exercise_id,
            exercise_name=exercise.name if exercise else None,
            exercise_description=exercise.description if exercise else None,
            sets=ex.sets,
            reps_min=ex.reps_min,
            reps_max=ex.reps_max,
            rest_seconds=ex.rest_seconds,
            order_index=ex.order_index,
            notes=ex.notes,
        ))
    return WorkoutPlanDayRead(
        plan_id=day.plan_id,
        day_of_week=day.day_of_week,
        focus=day.focus,
        is_rest=day.is_rest,
        exercises=ex_reads,
    )
