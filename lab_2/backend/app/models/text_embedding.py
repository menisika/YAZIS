from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from .base import Base

if TYPE_CHECKING:
    from .corpus_text import CorpusText


class TextEmbedding(Base):
    __tablename__ = "text_embeddings"
    __table_args__ = (UniqueConstraint("text_id", name="uq_text_embeddings_text_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text_id: Mapped[int] = mapped_column(Integer, ForeignKey("corpus_texts.id", ondelete="CASCADE"), nullable=False)
    embedding: Mapped[Optional[list]] = mapped_column(Vector(384), nullable=True)

    text: Mapped["CorpusText"] = relationship("CorpusText", back_populates="embedding")
