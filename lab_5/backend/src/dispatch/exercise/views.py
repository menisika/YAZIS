from fastapi import APIRouter, Query
from sqlmodel import select

from src.dispatch.auth.permissions import CurrentUser
from src.dispatch.database import SessionDep
from src.dispatch.exceptions import NotFoundError
from src.dispatch.exercise import service as exercise_service
from src.dispatch.exercise.models import Exercise, ExerciseRead, ExerciseVideoResponse
from src.dispatch.exercise.youtube import get_or_fetch_video_id
from src.dispatch.workout.models import WorkoutPlan, WorkoutPlanExercise

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=list[ExerciseRead])
def list_exercises(
    current_user: CurrentUser,
    db_session: SessionDep,
    muscle_group: str | None = None,
    category: str | None = None,
    equipment: str | None = None,
    difficulty: str | None = None,
    search: str | None = None,
    scope: str | None = None,  # "plan" → only exercises in user's active plan
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    if scope == "plan":
        # Find user's plan (unique per user)
        plan = db_session.exec(
            select(WorkoutPlan).where(WorkoutPlan.user_id == current_user.id)
        ).first()

        if not plan:
            return []

        # Collect exercise IDs referenced by this plan
        exercise_ids_stmt = (
            select(WorkoutPlanExercise.exercise_id)
            .where(WorkoutPlanExercise.plan_id == plan.id)
            .distinct()
        )
        exercise_ids = list(db_session.exec(exercise_ids_stmt).all())

        if not exercise_ids:
            return []

        stmt = select(Exercise).where(Exercise.id.in_(exercise_ids))
        if muscle_group:
            from src.dispatch.exercise.models import ExerciseMuscleGroup
            stmt = stmt.join(ExerciseMuscleGroup).where(
                ExerciseMuscleGroup.muscle_group == muscle_group
            )
        if search:
            stmt = stmt.where(Exercise.name.ilike(f"%{search}%"))

        exercises = db_session.exec(stmt.offset(offset).limit(limit)).all()
    else:
        exercises, _total = exercise_service.get_all(
            db_session=db_session,
            muscle_group=muscle_group,
            category=category,
            equipment=equipment,
            difficulty=difficulty,
            search=search,
            offset=offset,
            limit=limit,
        )

    result = []
    for ex in exercises:
        ex_read = exercise_service.get_exercise_with_muscles(
            db_session=db_session, exercise_id=ex.id
        )
        if ex_read:
            result.append(ex_read)
    return result


@router.get("/{exercise_id}", response_model=ExerciseRead)
def get_exercise(
    exercise_id: int,
    current_user: CurrentUser,
    db_session: SessionDep,
):
    ex = exercise_service.get_exercise_with_muscles(
        db_session=db_session, exercise_id=exercise_id
    )
    if not ex:
        raise NotFoundError("Exercise not found")
    return ex


@router.get("/{exercise_id}/video", response_model=ExerciseVideoResponse)
def get_exercise_video(
    exercise_id: int,
    current_user: CurrentUser,
    db_session: SessionDep,
):
    exercise = exercise_service.get(db_session=db_session, exercise_id=exercise_id)
    if not exercise:
        raise NotFoundError("Exercise not found")
    video_id = get_or_fetch_video_id(db_session=db_session, exercise=exercise)
    return ExerciseVideoResponse(youtube_video_id=video_id)
