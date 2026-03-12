from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class TextUploadMeta(BaseModel):
    title: str
    author: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    source_url: Optional[str] = None


class TextSummary(BaseModel):
    id: int
    title: str
    author: Optional[str]
    year: Optional[int]
    genre: Optional[str]
    source_url: Optional[str]
    token_count: int
    sentence_count: int
    created_at: Optional[str]

    model_config = {"from_attributes": True}
