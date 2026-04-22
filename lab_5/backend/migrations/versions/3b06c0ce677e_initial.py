"""initial

Revision ID: 3b06c0ce677e
Revises: 
Create Date: 2026-04-14 08:06:09.265287

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b06c0ce677e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("firebase_uid", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_firebase_uid"), "user", ["firebase_uid"], unique=True)

    op.create_table(
        "exercise",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("equipment", sa.String(), nullable=False),
        sa.Column("difficulty", sa.String(), nullable=False),
        sa.Column("instructions", sa.String(), nullable=False),
        sa.Column("met_value", sa.Float(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exercise_name"), "exercise", ["name"], unique=True)

    op.create_table(
        "user_profile",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("gender", sa.String(), nullable=False),
        sa.Column("height_cm", sa.Float(), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("fitness_level", sa.String(), nullable=False),
        sa.Column("preferred_workout_types", sa.JSON(), nullable=False),
        sa.Column("workout_days_per_week", sa.Integer(), nullable=False),
        sa.Column("session_duration_min", sa.Integer(), nullable=False),
        sa.Column("bmr", sa.Float(), nullable=False),
        sa.Column("tdee", sa.Float(), nullable=False),
        sa.Column("injuries", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_profile_user_id"), "user_profile", ["user_id"], unique=True)

    op.create_table(
        "exercise_muscle_group",
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("muscle_group", sa.String(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercise.id"]),
        sa.PrimaryKeyConstraint("exercise_id", "muscle_group"),
    )

    op.create_table(
        "workout_plan",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("plan_type", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workout_plan_user_id"), "workout_plan", ["user_id"], unique=False)

    op.create_table(
        "chat_conversation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_chat_conversation_user_id"), "chat_conversation", ["user_id"], unique=False)

    op.create_table(
        "workout_plan_day",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("focus", sa.String(), nullable=False),
        sa.Column("is_rest", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["workout_plan.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "chat_message",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["chat_conversation.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_chat_message_conversation_id"), "chat_message", ["conversation_id"], unique=False)

    op.create_table(
        "workout_plan_exercise",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plan_day_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("sets", sa.Integer(), nullable=False),
        sa.Column("reps_min", sa.Integer(), nullable=False),
        sa.Column("reps_max", sa.Integer(), nullable=False),
        sa.Column("rest_seconds", sa.Integer(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercise.id"]),
        sa.ForeignKeyConstraint(["plan_day_id"], ["workout_plan_day.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "workout_session",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plan_day_id", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("estimated_calories", sa.Float(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["plan_day_id"], ["workout_plan_day.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workout_session_user_id"), "workout_session", ["user_id"], unique=False)

    op.create_table(
        "session_set",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("set_number", sa.Integer(), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("reps", sa.Integer(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("rpe", sa.Integer(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercise.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["workout_session.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_session_set_session_id"), "session_set", ["session_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_session_set_session_id"), table_name="session_set")
    op.drop_table("session_set")
    op.drop_index(op.f("ix_workout_session_user_id"), table_name="workout_session")
    op.drop_table("workout_session")
    op.drop_table("workout_plan_exercise")
    op.drop_index(op.f("ix_chat_message_conversation_id"), table_name="chat_message")
    op.drop_table("chat_message")
    op.drop_table("workout_plan_day")
    op.drop_index(op.f("ix_chat_conversation_user_id"), table_name="chat_conversation")
    op.drop_table("chat_conversation")
    op.drop_index(op.f("ix_workout_plan_user_id"), table_name="workout_plan")
    op.drop_table("workout_plan")
    op.drop_table("exercise_muscle_group")
    op.drop_index(op.f("ix_user_profile_user_id"), table_name="user_profile")
    op.drop_table("user_profile")
    op.drop_index(op.f("ix_exercise_name"), table_name="exercise")
    op.drop_table("exercise")
    op.drop_index(op.f("ix_user_firebase_uid"), table_name="user")
    op.drop_table("user")
