from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sentence_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sentences.id", ondelete="CASCADE"), nullable=False, index=True
    )
    index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    lemma: Mapped[str] = mapped_column(String(500), nullable=False)
    pos: Mapped[str] = mapped_column(String(20), nullable=False)
    tag: Mapped[str] = mapped_column(String(30), nullable=False)
    dep: Mapped[str] = mapped_column(String(30), nullable=False)
    head_index: Mapped[int] = mapped_column(Integer, nullable=False)
    is_stop: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_punct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ent_type: Mapped[str] = mapped_column(String(50), nullable=False, default="")

    sentence: Mapped["Sentence"] = relationship("Sentence", back_populates="tokens")  # noqa: F821
