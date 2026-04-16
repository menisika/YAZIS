from pydantic import BaseModel

from .sentence import SentenceListItem


class PatternQuery(BaseModel):
    source_pos: str
    dep_rel: str
    target_pos: str


class PatternMatch(BaseModel):
    sentence: SentenceListItem
    source_token_index: int
    target_token_index: int
    source_text: str
    target_text: str


class PatternSearchResponse(BaseModel):
    query: PatternQuery
    total: int
    matches: list[PatternMatch]
