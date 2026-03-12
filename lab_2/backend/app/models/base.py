from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, mapped_column, MappedColumn
from sqlalchemy import DateTime


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
