"""spaCy NLP pipeline wrapper — model name comes from settings."""
from __future__ import annotations

from typing import Any
import spacy
from spacy.language import Language


_nlp_cache: dict[str, Language] = {}


def get_nlp(model_name: str) -> Language:
    if model_name not in _nlp_cache:
        _nlp_cache[model_name] = spacy.load(model_name)
    return _nlp_cache[model_name]


def process_text(raw: str, model_name: str) -> spacy.tokens.Doc:
    nlp = get_nlp(model_name)
    return nlp(raw)


def doc_to_sentences(doc: spacy.tokens.Doc) -> list[dict[str, Any]]:
    sentences = []
    for idx, sent in enumerate(doc.sents):
        sentences.append(
            {
                "sentence_index": idx,
                "content": sent.text,
            }
        )
    return sentences


def doc_to_tokens(doc: spacy.tokens.Doc) -> list[dict[str, Any]]:
    tokens = []
    sent_map: dict[int, int] = {}  # spacy sentence start char -> sentence_index
    for idx, sent in enumerate(doc.sents):
        sent_map[sent.start] = idx

    token_index_global = 0
    for sent_idx, sent in enumerate(doc.sents):
        for tok_in_sent_idx, token in enumerate(sent):
            if token.is_space:
                continue
            morph: dict[str, list[str]] = {}
            for feat in token.morph:
                key, val = feat.split("=", 1)
                morph.setdefault(key, []).append(val)

            tokens.append(
                {
                    "surface": token.text,
                    "lemma": token.lemma_.lower(),
                    "pos": token.pos_,
                    "tag": token.tag_,
                    "morph": morph if morph else None,
                    "sentence_index": sent_idx,
                    "token_index": token_index_global,
                    "char_start": token.idx,
                    "char_end": token.idx + len(token.text),
                }
            )
            token_index_global += 1
    return tokens


def doc_to_entities(doc: spacy.tokens.Doc) -> list[dict[str, Any]]:
    entities = []
    sent_boundaries: list[tuple[int, int, int]] = []
    for idx, sent in enumerate(doc.sents):
        sent_boundaries.append((sent.start_char, sent.end_char, idx))

    def find_sent_index(start_char: int) -> int | None:
        for s_start, s_end, s_idx in sent_boundaries:
            if s_start <= start_char < s_end:
                return s_idx
        return None

    for ent in doc.ents:
        entities.append(
            {
                "entity_text": ent.text,
                "label": ent.label_,
                "start_char": ent.start_char,
                "end_char": ent.end_char,
                "sentence_index": find_sent_index(ent.start_char),
            }
        )
    return entities
