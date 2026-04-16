"""add_semantic_columns

Revision ID: a1b2c3d4e5f6
Revises: 71e854d78bd9
Create Date: 2026-04-09 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "71e854d78bd9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("tokens", sa.Column("semantic_role", sa.String(20), nullable=True))
    op.add_column("tokens", sa.Column("semantic_label", sa.String(50), nullable=True))
    op.add_column("tokens", sa.Column("is_anomalous", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("tokens", sa.Column("anomaly_reason", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("tokens", "anomaly_reason")
    op.drop_column("tokens", "is_anomalous")
    op.drop_column("tokens", "semantic_label")
    op.drop_column("tokens", "semantic_role")
