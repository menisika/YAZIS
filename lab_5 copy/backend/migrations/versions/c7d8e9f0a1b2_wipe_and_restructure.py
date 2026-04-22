"""wipe_and_restructure

Revision ID: c7d8e9f0a1b2
Revises: a3f9e2b1c4d7
Create Date: 2026-04-17 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "c7d8e9f0a1b2"
down_revision: Union[str, None] = "a3f9e2b1c4d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Step 1: Wipe all data ────────────────────────────────────────────────
    op.execute("DELETE FROM session_set")
    op.execute("DELETE FROM workout_session")
    op.execute("DELETE FROM workout_plan_exercise")
    op.execute("DELETE FROM workout_plan_day")
    op.execute("DELETE FROM workout_plan")
    op.execute("DELETE FROM exercise_muscle_group")
    op.execute("DELETE FROM exercise")

    # ── Step 2: Clean up exercise table ─────────────────────────────────────
    op.drop_column("exercise", "image_url")

    # ── Step 3: workout_plan — enforce one-plan-per-user ────────────────────
    op.create_unique_constraint("uq_workout_plan_user_id", "workout_plan", ["user_id"])

    # ── Step 4: workout_session — replace plan_day_id with plan_id + dow ────
    # Drop the FK to workout_plan_day dynamically (name varies by DB creation method)
    op.execute("""
        DO $$
        DECLARE
            cname text;
        BEGIN
            SELECT conname INTO cname
            FROM pg_constraint
            WHERE conrelid = 'workout_session'::regclass
              AND contype = 'f'
              AND confrelid = 'workout_plan_day'::regclass;
            IF cname IS NOT NULL THEN
                EXECUTE format('ALTER TABLE workout_session DROP CONSTRAINT %I', cname);
            END IF;
        END $$;
    """)
    op.drop_column("workout_session", "plan_day_id")
    op.add_column("workout_session", sa.Column("plan_id", sa.Integer(), nullable=True))
    op.add_column("workout_session", sa.Column("plan_day_of_week", sa.Integer(), nullable=True))

    # ── Step 5: Rebuild workout_plan_exercise ────────────────────────────────
    op.drop_table("workout_plan_exercise")

    # ── Step 6: Rebuild workout_plan_day with composite PK ──────────────────
    op.drop_table("workout_plan_day")

    op.create_table(
        "workout_plan_day",
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("focus", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default=""),
        sa.Column("is_rest", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["plan_id"], ["workout_plan.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("plan_id", "day_of_week"),
    )

    op.create_table(
        "workout_plan_exercise",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("sets", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("reps_min", sa.Integer(), nullable=False, server_default="8"),
        sa.Column("reps_max", sa.Integer(), nullable=False, server_default="12"),
        sa.Column("rest_seconds", sa.Integer(), nullable=False, server_default="90"),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(
            ["plan_id", "day_of_week"],
            ["workout_plan_day.plan_id", "workout_plan_day.day_of_week"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercise.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workout_plan_exercise_plan_id", "workout_plan_exercise", ["plan_id"])
    op.create_index("ix_workout_plan_exercise_day_of_week", "workout_plan_exercise", ["day_of_week"])


def downgrade() -> None:
    pass
