"""Stem extraction (Porter / Snowball)."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from utils.logging_config import get_logger

logger = get_logger("core.stem_extractor")


class StemExtractor:
    """Stem extraction using NLTK's Porter or Snowball stemmer.

    Args:
        algorithm: ``'porter'`` or ``'snowball'`` (default).
    """

    def __init__(self, algorithm: str = "snowball") -> None:
        self._algorithm = algorithm
        self._stemmer: Any

        if algorithm == "porter":
            from nltk.stem import PorterStemmer  # type: ignore[import-untyped]
            self._stemmer = PorterStemmer()
        else:
            from nltk.stem import SnowballStemmer  # type: ignore[import-untyped]
            self._stemmer = SnowballStemmer("english")

        logger.debug("StemExtractor initialized with %s algorithm", algorithm)

    @lru_cache(maxsize=10_000)
    def extract(self, word: str) -> str:
        """Extract the stem of a word.

        Args:
            word: Lowercased word.

        Returns:
            The stemmed form.
        """
        return self._stemmer.stem(word.lower())

    def extract_batch(self, words: list[str]) -> dict[str, str]:
        """Extract stems for a batch of words.

        Args:
            words: List of words.

        Returns:
            ``{word: stem}`` mapping.
        """
        return {w: self.extract(w) for w in words}

    @property
    def algorithm(self) -> str:
        return self._algorithm
