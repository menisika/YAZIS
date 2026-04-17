"""add cascade delete to chat_message conversation_id fk

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-04-18

"""
from typing import Sequence, Union

from alembic import op

revision: str = "e2f3a4b5c6d7"
down_revision: Union[str, None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "chat_message_conversation_id_fkey",
        "chat_message",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "chat_message_conversation_id_fkey",
        "chat_message",
        "chat_conversation",
        ["conversation_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "chat_message_conversation_id_fkey",
        "chat_message",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "chat_message_conversation_id_fkey",
        "chat_message",
        "chat_conversation",
        ["conversation_id"],
        ["id"],
    )
