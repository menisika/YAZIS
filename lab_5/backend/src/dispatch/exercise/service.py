from sqlmodel import Session, func, select

from src.dispatch.exercise.models import (
    Exercise,
    ExerciseMuscleGroup,
    ExerciseRead,
    MuscleGroupRead,
)


def get(*, db_session: Session, exercise_id: int) -> Exercise | None:
    return db_session.get(Exercise, exercise_id)


def get_all(
    *,
    db_session: Session,
    muscle_group: str | None = None,
    category: str | None = None,
    equipment: str | None = None,
    difficulty: str | None = None,
    search: str | None = None,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[Exercise], int]:
    statement = select(Exercise)

    if muscle_group:
        statement = statement.join(ExerciseMuscleGroup).where(
            ExerciseMuscleGroup.muscle_group == muscle_group
        )
    if category:
        statement = statement.where(Exercise.category == category)
    if equipment:
        statement = statement.where(Exercise.equipment == equipment)
    if difficulty:
        statement = statement.where(Exercise.difficulty == difficulty)
    if search:
        statement = statement.where(Exercise.name.ilike(f"%{search}%"))

    # Count
    count_stmt = select(func.count()).select_from(statement.subquery())
    total = db_session.exec(count_stmt).one()

    # Paginate
    exercises = db_session.exec(statement.offset(offset).limit(limit)).all()
    return exercises, total


def get_muscle_groups(*, db_session: Session, exercise_id: int) -> list[ExerciseMuscleGroup]:
    statement = select(ExerciseMuscleGroup).where(
        ExerciseMuscleGroup.exercise_id == exercise_id
    )
    return list(db_session.exec(statement).all())


def get_exercise_with_muscles(*, db_session: Session, exercise_id: int) -> ExerciseRead | None:
    exercise = get(db_session=db_session, exercise_id=exercise_id)
    if not exercise:
        return None
    muscles = get_muscle_groups(db_session=db_session, exercise_id=exercise_id)
    return ExerciseRead(
        **exercise.model_dump(),
        muscle_groups=[MuscleGroupRead(muscle_group=m.muscle_group, is_primary=m.is_primary) for m in muscles],
    )


def get_exercises_by_muscle_group(
    *,
    db_session: Session,
    muscle_group: str,
    difficulty: str | None = None,
    is_primary: bool = True,
) -> list[Exercise]:
    statement = (
        select(Exercise)
        .join(ExerciseMuscleGroup)
        .where(ExerciseMuscleGroup.muscle_group == muscle_group)
        .where(ExerciseMuscleGroup.is_primary == is_primary)
    )
    if difficulty:
        statement = statement.where(Exercise.difficulty == difficulty)
    return list(db_session.exec(statement).all())
