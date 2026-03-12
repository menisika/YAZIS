from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .corpus_text import CorpusText
    from .sentence import Sentence


class NamedEntity(Base):
    __tablename__ = "named_entities"
    __table_args__ = (
        Index("ix_named_entities_text_id", "text_id"),
        Index("ix_named_entities_label", "label"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text_id: Mapped[int] = mapped_column(Integer, ForeignKey("corpus_texts.id", ondelete="CASCADE"), nullable=False)
    sentence_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sentences.id", ondelete="SET NULL"), nullable=True)
    entity_text: Mapped[str] = mapped_column(String(1024), nullable=False)
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    start_char: Mapped[int] = mapped_column(Integer, nullable=False)
    end_char: Mapped[int] = mapped_column(Integer, nullable=False)

    text: Mapped["CorpusText"] = relationship("CorpusText", back_populates="named_entities")
    sentence: Mapped[Optional["Sentence"]] = relationship("Sentence", back_populates="named_entities")
