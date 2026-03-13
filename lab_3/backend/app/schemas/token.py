from pydantic import BaseModel


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

    model_config = {"from_attributes": True}
