from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .sentence import Sentence
    from .token import Token
    from .named_entity import NamedEntity
    from .text_embedding import TextEmbedding


class CorpusText(Base, TimestampMixin):
    __tablename__ = "corpus_texts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    author: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    genre: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sentence_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    sentences: Mapped[List["Sentence"]] = relationship(
        "Sentence", back_populates="text", cascade="all, delete-orphan"
    )
    tokens: Mapped[List["Token"]] = relationship(
        "Token", back_populates="text", cascade="all, delete-orphan"
    )
    named_entities: Mapped[List["NamedEntity"]] = relationship(
        "NamedEntity", back_populates="text", cascade="all, delete-orphan"
    )
    embedding: Mapped[Optional["TextEmbedding"]] = relationship(
        "TextEmbedding", back_populates="text", cascade="all, delete-orphan", uselist=False
    )
