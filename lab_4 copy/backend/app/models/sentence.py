from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Sentence(Base):
    __tablename__ = "sentences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    complexity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    document: Mapped["Document"] = relationship("Document", back_populates="sentences")  # noqa: F821
    tokens: Mapped[list["Token"]] = relationship(  # noqa: F821
        "Token", back_populates="sentence", cascade="all, delete-orphan", lazy="select", order_by="Token.index"
    )
