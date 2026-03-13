"""NLP service wrapping spaCy — loaded once at app startup."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from functools import partial

import spacy
from spacy.language import Language

_nlp: Language | None = None


def load_model(model_name: str) -> None:
    global _nlp
    _nlp = spacy.load(model_name)


def get_nlp() -> Language:
    if _nlp is None:
        raise RuntimeError("spaCy model not loaded. Call load_model() during app startup.")
    return _nlp


@dataclass
class TokenData:
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


@dataclass
class SentenceData:
    index: int
    text: str
    tokens: list[TokenData] = field(default_factory=list)


def _parse_sync(text: str) -> list[SentenceData]:
    nlp = get_nlp()
    doc = nlp(text)
    sentences: list[SentenceData] = []
    for sent_idx, sent in enumerate(doc.sents):
        tokens: list[TokenData] = []
        # token.i is global index; we want sentence-local index
        offset = sent.start
        for tok in sent:
            tokens.append(
                TokenData(
                    index=tok.i - offset,
                    text=tok.text,
                    lemma=tok.lemma_,
                    pos=tok.pos_,
                    tag=tok.tag_,
                    dep=tok.dep_,
                    head_index=tok.head.i - offset,
                    is_stop=tok.is_stop,
                    is_punct=tok.is_punct,
                    ent_type=tok.ent_type_,
                )
            )
        sentences.append(SentenceData(index=sent_idx, text=sent.text, tokens=tokens))
    return sentences


async def process_text(text: str) -> list[SentenceData]:
    """Run spaCy pipeline in a thread pool (CPU-bound)."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(_parse_sync, text))
