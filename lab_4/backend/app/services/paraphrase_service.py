"""Paraphrase service — replaces content words with WordNet synonyms."""
from __future__ import annotations

from dataclasses import dataclass

from nltk.corpus import wordnet as wn

from app.services.nlp_service import TokenData

# Map spaCy POS tags to WordNet POS constants
_SPACY_TO_WN: dict[str, str] = {
    "NOUN": wn.NOUN,
    "VERB": wn.VERB,
    "ADJ": wn.ADJ,
    "ADV": wn.ADV,
}


@dataclass
class ParaphraseChange:
    index: int
    original_text: str
    synonym: str


@dataclass
class ParaphraseResult:
    original: str
    paraphrased: str
    changes: list[ParaphraseChange]


def _get_first_synonym(word: str, pos: str) -> str | None:
    """Return the first WordNet synonym for word that differs from the original."""
    wn_pos = _SPACY_TO_WN.get(pos)
    if wn_pos is None:
        return None
    synsets = wn.synsets(word.lower(), pos=wn_pos)
    for synset in synsets:
        for lemma in synset.lemmas():
            candidate = lemma.name().replace("_", " ")
            if candidate.lower() != word.lower() and " " not in candidate:
                return candidate
    return None


def generate_paraphrase(sentence_text: str, tokens: list[TokenData]) -> ParaphraseResult:
    """Build a paraphrased sentence by substituting content words with synonyms."""
    changes: list[ParaphraseChange] = []
    word_replacements: dict[int, str] = {}  # token.index → synonym

    for token in tokens:
        if token.is_stop or token.is_punct:
            continue
        if token.pos not in _SPACY_TO_WN:
            continue
        synonym = _get_first_synonym(token.lemma, token.pos)
        if synonym:
            changes.append(ParaphraseChange(
                index=token.index,
                original_text=token.text,
                synonym=synonym,
            ))
            word_replacements[token.index] = synonym

    # Reconstruct sentence by replacing tokens with synonyms
    if not word_replacements:
        return ParaphraseResult(
            original=sentence_text,
            paraphrased=sentence_text,
            changes=[],
        )

    parts: list[str] = []
    for token in sorted(tokens, key=lambda t: t.index):
        replacement = word_replacements.get(token.index)
        # Preserve original capitalisation for sentence-start tokens
        if replacement:
            if token.index == 0 or (token.text and token.text[0].isupper()):
                replacement = replacement.capitalize()
            parts.append(replacement)
        else:
            parts.append(token.text)

    paraphrased = " ".join(parts)

    return ParaphraseResult(
        original=sentence_text,
        paraphrased=paraphrased,
        changes=changes,
    )
