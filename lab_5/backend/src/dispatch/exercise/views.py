from fastapi import APIRouter, Query

from src.dispatch.auth.permissions import CurrentUser
from src.dispatch.database import SessionDep
from src.dispatch.exceptions import NotFoundError
from src.dispatch.exercise import service as exercise_service
from src.dispatch.exercise.models import ExerciseRead, ExerciseVideoResponse
from src.dispatch.exercise.youtube import get_or_fetch_video_id

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
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
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
    # Enrich with muscle groups
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
