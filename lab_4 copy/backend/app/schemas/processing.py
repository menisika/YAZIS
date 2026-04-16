from pydantic import BaseModel


class ProcessingSummary(BaseModel):
    document_id: int
    filename: str
    sentence_count: int
    token_count: int
    parse_duration_ms: float
