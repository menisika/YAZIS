"""add_exercise_slug

Revision ID: a3f9e2b1c4d7
Revises: 5d1346d35deb
Create Date: 2026-04-16 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a3f9e2b1c4d7"
down_revision: Union[str, None] = "5d1346d35deb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "exercise",
        sa.Column("slug", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.create_index("ix_exercise_slug", "exercise", ["slug"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_exercise_slug", table_name="exercise")
    op.drop_column("exercise", "slug")
