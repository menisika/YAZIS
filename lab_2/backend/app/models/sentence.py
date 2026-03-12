from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Integer, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from .base import Base

if TYPE_CHECKING:
    from .corpus_text import CorpusText
    from .token import Token
    from .named_entity import NamedEntity


class Sentence(Base):
    __tablename__ = "sentences"
    __table_args__ = (
        Index("ix_sentences_text_id", "text_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text_id: Mapped[int] = mapped_column(Integer, ForeignKey("corpus_texts.id", ondelete="CASCADE"), nullable=False)
    sentence_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[list]] = mapped_column(Vector(384), nullable=True)

    text: Mapped["CorpusText"] = relationship("CorpusText", back_populates="sentences")
    tokens: Mapped[List["Token"]] = relationship("Token", back_populates="sentence")
    named_entities: Mapped[List["NamedEntity"]] = relationship("NamedEntity", back_populates="sentence")
