from pydantic import BaseModel

from .token import TokenResponse


class SentenceListItem(BaseModel):
    id: int
    document_id: int
    index: int
    text: str
    complexity_score: float
    token_count: int

    model_config = {"from_attributes": True}


class SentenceResponse(BaseModel):
    id: int
    document_id: int
    index: int
    text: str
    complexity_score: float
    token_count: int
    tokens: list[TokenResponse] = []

    model_config = {"from_attributes": True}
