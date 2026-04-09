from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_format: str
    uploaded_at: datetime
    word_count: int
    sentence_count: int

    model_config = {"from_attributes": True}


class DocumentListItem(BaseModel):
    id: int
    filename: str
    original_format: str
    uploaded_at: datetime
    word_count: int
    sentence_count: int
    avg_complexity: float
    total_tokens: int

    model_config = {"from_attributes": True}
