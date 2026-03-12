"""Initial schema with pgvector extension

Revision ID: 0001
Revises:
Create Date: 2026-03-12

"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "corpus_texts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("author", sa.String(256), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("genre", sa.String(128), nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sentence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "sentences",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("text_id", sa.Integer(), nullable=False),
        sa.Column("sentence_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.ForeignKeyConstraint(["text_id"], ["corpus_texts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sentences_text_id", "sentences", ["text_id"])
    op.execute(
        "CREATE INDEX ix_sentences_embedding_hnsw ON sentences USING hnsw (embedding vector_cosine_ops)"
    )

    op.create_table(
        "tokens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("text_id", sa.Integer(), nullable=False),
        sa.Column("sentence_id", sa.Integer(), nullable=True),
        sa.Column("surface", sa.String(512), nullable=False),
        sa.Column("lemma", sa.String(512), nullable=False),
        sa.Column("pos", sa.String(64), nullable=False),
        sa.Column("tag", sa.String(64), nullable=False),
        sa.Column("morph", postgresql.JSONB(), nullable=True),
        sa.Column("sentence_index", sa.Integer(), nullable=False),
        sa.Column("token_index", sa.Integer(), nullable=False),
        sa.Column("char_start", sa.Integer(), nullable=False),
        sa.Column("char_end", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["text_id"], ["corpus_texts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sentence_id"], ["sentences.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tokens_text_id_lemma", "tokens", ["text_id", "lemma"])
    op.create_index("ix_tokens_lemma", "tokens", ["lemma"])
    op.create_index("ix_tokens_pos", "tokens", ["pos"])
    op.create_index("ix_tokens_surface", "tokens", ["surface"])

    op.create_table(
        "named_entities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("text_id", sa.Integer(), nullable=False),
        sa.Column("sentence_id", sa.Integer(), nullable=True),
        sa.Column("entity_text", sa.String(1024), nullable=False),
        sa.Column("label", sa.String(64), nullable=False),
        sa.Column("start_char", sa.Integer(), nullable=False),
        sa.Column("end_char", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["text_id"], ["corpus_texts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sentence_id"], ["sentences.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_named_entities_text_id", "named_entities", ["text_id"])
    op.create_index("ix_named_entities_label", "named_entities", ["label"])

    op.create_table(
        "text_embeddings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("text_id", sa.Integer(), nullable=False),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.ForeignKeyConstraint(["text_id"], ["corpus_texts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("text_id", name="uq_text_embeddings_text_id"),
    )


def downgrade() -> None:
    op.drop_table("text_embeddings")
    op.drop_table("named_entities")
    op.drop_table("tokens")
    op.drop_table("sentences")
    op.drop_table("corpus_texts")
    op.execute("DROP EXTENSION IF EXISTS vector")
