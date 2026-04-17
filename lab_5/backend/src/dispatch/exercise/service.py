import re

from sqlmodel import Session, func, select

from src.dispatch.exercise.models import (
    Exercise,
    ExerciseMuscleGroup,
    ExerciseRead,
    MuscleGroupRead,
)


def slugify(name: str) -> str:
    """Normalize exercise name to a canonical slug."""
    name = name.lower().strip()
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", "_", name)
    return name


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


def get_all_names(*, db_session: Session) -> list[str]:
    """Return all exercise names currently in the DB."""
    rows = db_session.exec(select(Exercise.name)).all()
    return list(rows)


def get_by_slugs(*, db_session: Session, slugs: list[str]) -> dict[str, Exercise]:
    """Return {slug: Exercise} map for all matching slugs."""
    if not slugs:
        return {}
    statement = select(Exercise).where(Exercise.slug.in_(slugs))
    exercises = db_session.exec(statement).all()
    return {ex.slug: ex for ex in exercises if ex.slug is not None}


def get_by_name(*, db_session: Session, name: str) -> Exercise | None:
    """Return an Exercise by exact name, or None."""
    return db_session.exec(select(Exercise).where(Exercise.name == name)).first()


def create_with_muscles(*, db_session: Session, data: object) -> Exercise:
    """Create an Exercise row with its muscle group associations.

    `data` must have: name, slug, description, instructions, category,
    equipment, difficulty, met_value, muscle_groups (list[str]),
    primary_muscles (list[str]).

    If an exercise with the same name already exists, returns it (get-or-create).
    """
    existing = get_by_name(db_session=db_session, name=data.name)
    if existing:
        return existing

    exercise = Exercise(
        name=data.name,
        slug=data.slug,
        description=data.description,
        instructions=data.instructions,
        category=data.category,
        equipment=data.equipment,
        difficulty=data.difficulty,
        met_value=data.met_value,
    )
    db_session.add(exercise)
    db_session.flush()  # assign ID without committing

    for mg in data.muscle_groups:
        is_primary = mg in data.primary_muscles
        db_session.add(ExerciseMuscleGroup(
            exercise_id=exercise.id,
            muscle_group=mg,
            is_primary=is_primary,
        ))

    db_session.commit()
    db_session.refresh(exercise)
    return exercise
