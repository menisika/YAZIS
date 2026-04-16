"""Load exercises from JSON into database."""

import json
from pathlib import Path

from sqlmodel import Session, select

from src.dispatch.exercise.models import Exercise, ExerciseMuscleGroup


def seed_exercises(db_session: Session) -> int:
    """Seed exercises from exercises.json. Returns count of inserted exercises."""
    json_path = Path(__file__).parent / "exercises.json"
    if not json_path.exists():
        print("exercises.json not found, skipping seed")
        return 0

    with open(json_path) as f:
        exercises_data = json.load(f)

    count = 0
    for ex_data in exercises_data:
        # Check if exercise already exists
        stmt = select(Exercise).where(Exercise.name == ex_data["name"])
        existing = db_session.exec(stmt).first()
        if existing:
            continue

        exercise = Exercise(
            name=ex_data["name"],
            description=ex_data.get("description", ""),
            category=ex_data["category"],
            equipment=ex_data["equipment"],
            difficulty=ex_data["difficulty"],
            image_url=ex_data.get("image_url"),
            instructions=ex_data.get("instructions", ""),
            met_value=ex_data.get("met_value", 3.5),
        )
        db_session.add(exercise)
        db_session.commit()
        db_session.refresh(exercise)

        for mg in ex_data.get("muscle_groups", []):
            muscle = ExerciseMuscleGroup(
                exercise_id=exercise.id,
                muscle_group=mg["muscle_group"],
                is_primary=mg.get("is_primary", True),
            )
            db_session.add(muscle)

        db_session.commit()
        count += 1

    return count


if __name__ == "__main__":
    from src.dispatch.database import engine

    with Session(engine) as session:
        inserted = seed_exercises(session)
        print(f"Seeded {inserted} exercises")
