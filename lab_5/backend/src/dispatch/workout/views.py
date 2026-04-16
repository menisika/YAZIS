from fastapi import APIRouter

from src.dispatch.auth.permissions import CurrentUser
from src.dispatch.database import SessionDep
from src.dispatch.exceptions import NotFoundError
from src.dispatch.workout import service as workout_service
from src.dispatch.workout.flows import generate_plan_flow
from src.dispatch.workout.models import (
    GenerateWorkoutRequest,
    WorkoutPlanDayRead,
    WorkoutPlanRead,
)

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("/generate")
async def generate_workout(
    body: GenerateWorkoutRequest,
    current_user: CurrentUser,
    db_session: SessionDep,
):
    result = await generate_plan_flow(
        db_session=db_session,
        user_id=current_user.id,
        week_start=body.week_start,
        focus_muscle_groups=body.focus_muscle_groups,
        exclude_exercises=body.exclude_exercises,
    )
    return result


@router.get("", response_model=list[WorkoutPlanRead])
def list_workouts(current_user: CurrentUser, db_session: SessionDep):
    plans = workout_service.get_all(db_session=db_session, user_id=current_user.id)
    return [
        workout_service.get_plan_read(db_session=db_session, plan_id=p.id)
        for p in plans
    ]


@router.get("/today", response_model=WorkoutPlanDayRead | None)
def get_today_workout(current_user: CurrentUser, db_session: SessionDep):
    return workout_service.get_today_plan(
        db_session=db_session, user_id=current_user.id
    )


@router.get("/{plan_id}", response_model=WorkoutPlanRead)
def get_workout(plan_id: int, current_user: CurrentUser, db_session: SessionDep):
    plan = workout_service.get_plan_read(db_session=db_session, plan_id=plan_id)
    if not plan:
        raise NotFoundError("Workout plan not found")
    return plan


@router.delete("/{plan_id}")
def delete_workout(plan_id: int, current_user: CurrentUser, db_session: SessionDep):
    workout_service.delete(
        db_session=db_session, plan_id=plan_id, user_id=current_user.id
    )
    return {"ok": True}
