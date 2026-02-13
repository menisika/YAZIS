"""Lexical analysis: tokenization, lemmatization, and frequency counting."""

from __future__ import annotations

import re
from collections import Counter
from functools import lru_cache

import nltk  # type: ignore[import-untyped]
from nltk.stem import WordNetLemmatizer  # type: ignore[import-untyped]
from nltk.tokenize import word_tokenize  # type: ignore[import-untyped]

from models.enums import PartOfSpeech
from utils.helpers import normalize_text, strip_punctuation
from utils.logging_config import get_logger

logger = get_logger("core.lexical_analyzer")

# Lazy-initialized mapping from Penn Treebank POS to WordNet POS
_WN_POS_MAP: dict[str, str] | None = None


def _get_wn_pos_map() -> dict[str, str]:
    """Lazily build the Penn-to-WordNet POS mapping."""
    global _WN_POS_MAP
    if _WN_POS_MAP is None:
        from nltk.corpus import wordnet  # type: ignore[import-untyped]
        _WN_POS_MAP = {
            "N": wordnet.NOUN,
            "V": wordnet.VERB,
            "J": wordnet.ADJ,
            "R": wordnet.ADV,
        }
    return _WN_POS_MAP

# Tokens to ignore (punctuation, numbers-only, single chars)
_SKIP_PATTERN = re.compile(r"^[\W\d_]+$|^.$")


class LexicalAnalyzer:
    """Tokenize text, extract unique lemmas, and count frequencies.

    Uses NLTK ``word_tokenize`` for tokenization and ``WordNetLemmatizer``
    for lemmatization.
    """

    def __init__(self) -> None:
        self._lemmatizer = WordNetLemmatizer()

    def tokenize(self, text: str) -> list[str]:
        """Tokenize raw text into lowercase word tokens.

        Args:
            text: Input text.

        Returns:
            List of lowercased word tokens with punctuation stripped.
        """
        text = normalize_text(text)
        raw_tokens = word_tokenize(text)
        tokens: list[str] = []
        for tok in raw_tokens:
            tok = strip_punctuation(tok).lower()
            if tok and not _SKIP_PATTERN.match(tok):
                tokens.append(tok)
        logger.debug("Tokenized %d tokens from %d characters", len(tokens), len(text))
        return tokens

    def pos_tag(self, tokens: list[str]) -> list[tuple[str, str]]:
        """POS-tag a list of tokens using NLTK's averaged perceptron tagger.

        Args:
            tokens: List of word tokens.

        Returns:
            List of ``(token, POS_tag)`` tuples.
        """
        return nltk.pos_tag(tokens)

    @lru_cache(maxsize=10_000)
    def lemmatize(self, word: str, penn_tag: str = "NN") -> str:
        """Lemmatize a single word given its Penn Treebank POS tag.

        Args:
            word: Lowercased word.
            penn_tag: Penn Treebank POS tag.

        Returns:
            The lemma (base form).
        """
        pos_map = _get_wn_pos_map()
        wn_pos = pos_map.get(penn_tag[0], "n")
        return self._lemmatizer.lemmatize(word, pos=wn_pos)

    def extract_lexemes(
        self, text: str
    ) -> tuple[dict[str, int], dict[str, PartOfSpeech], dict[str, list[str]]]:
        """Full lexeme extraction pipeline.

        Args:
            text: Raw document text.

        Returns:
            A tuple of:
            - ``freq``: ``{lemma: count}`` frequency map.
            - ``pos_map``: ``{lemma: PartOfSpeech}`` most-common POS per lemma.
            - ``forms_map``: ``{lemma: [original_tokens]}`` mapping lemma to
              all original token forms seen in the text.
        """
        tokens = self.tokenize(text)
        tagged = self.pos_tag(tokens)

        lemma_counter: Counter[str] = Counter()
        pos_counter: dict[str, Counter[PartOfSpeech]] = {}
        forms_map: dict[str, set[str]] = {}

        for token, tag in tagged:
            lemma = self.lemmatize(token, tag)
            lemma_counter[lemma] += 1

            pos = PartOfSpeech.from_penn(tag)
            pos_counter.setdefault(lemma, Counter())[pos] += 1
            forms_map.setdefault(lemma, set()).add(token)

        # Pick most common POS for each lemma
        pos_map: dict[str, PartOfSpeech] = {}
        for lemma, counter in pos_counter.items():
            pos_map[lemma] = counter.most_common(1)[0][0]

        freq = dict(lemma_counter)
        forms_out = {k: sorted(v) for k, v in forms_map.items()}

        logger.info(
            "Extracted %d unique lexemes from %d tokens",
            len(freq), len(tokens),
        )
        return freq, pos_map, forms_out
