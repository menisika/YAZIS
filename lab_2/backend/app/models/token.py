from __future__ import annotations
from typing import Optional, Any, TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .corpus_text import CorpusText
    from .sentence import Sentence


class Token(Base):
    __tablename__ = "tokens"
    __table_args__ = (
        Index("ix_tokens_text_id_lemma", "text_id", "lemma"),
        Index("ix_tokens_lemma", "lemma"),
        Index("ix_tokens_pos", "pos"),
        Index("ix_tokens_surface", "surface"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text_id: Mapped[int] = mapped_column(Integer, ForeignKey("corpus_texts.id", ondelete="CASCADE"), nullable=False)
    sentence_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sentences.id", ondelete="SET NULL"), nullable=True)
    surface: Mapped[str] = mapped_column(String(512), nullable=False)
    lemma: Mapped[str] = mapped_column(String(512), nullable=False)
    pos: Mapped[str] = mapped_column(String(64), nullable=False)
    tag: Mapped[str] = mapped_column(String(64), nullable=False)
    morph: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    sentence_index: Mapped[int] = mapped_column(Integer, nullable=False)
    token_index: Mapped[int] = mapped_column(Integer, nullable=False)
    char_start: Mapped[int] = mapped_column(Integer, nullable=False)
    char_end: Mapped[int] = mapped_column(Integer, nullable=False)

    text: Mapped["CorpusText"] = relationship("CorpusText", back_populates="tokens")
    sentence: Mapped[Optional["Sentence"]] = relationship("Sentence", back_populates="tokens")
