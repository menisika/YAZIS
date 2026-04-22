from datetime import datetime

from sqlmodel import Field, SQLModel


class TimeStampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
