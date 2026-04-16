from pydantic import BaseModel


class ConceptNetEdge(BaseModel):
    relation: str
    start_label: str
    end_label: str
    weight: float


class ConceptNetResponse(BaseModel):
    word: str
    edges: list[ConceptNetEdge]


class ParaphraseChange(BaseModel):
    index: int
    original_text: str
    synonym: str


class ParaphraseResponse(BaseModel):
    original: str
    paraphrased: str
    changes: list[ParaphraseChange]


class WordNetResponse(BaseModel):
    word: str
    definition: str | None = None
    synonyms: list[str] = []
