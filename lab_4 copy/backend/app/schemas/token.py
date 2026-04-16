from typing import Optional
from pydantic import BaseModel, field_validator


class TokenResponse(BaseModel):
    id: int
    sentence_id: int
    index: int
    text: str
    lemma: str
    pos: str
    tag: str
    dep: str
    head_index: int
    is_stop: bool
    is_punct: bool
    ent_type: str
    # Semantic fields (empty string / False for legacy tokens without semantic analysis)
    semantic_role: str = ""
    semantic_label: str = ""
    is_anomalous: bool = False
    anomaly_reason: Optional[str] = ""

    @field_validator("anomaly_reason", "semantic_role", "semantic_label", mode="before")
    @classmethod
    def none_to_empty(cls, v: Optional[str]) -> str:
        return v if v is not None else ""

    model_config = {"from_attributes": True}
