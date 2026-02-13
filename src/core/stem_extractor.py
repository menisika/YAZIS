"""Stem extraction wrappers (Porter / Snowball)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache

from utils.logging_config import get_logger

logger = get_logger("core.stem_extractor")


class Stemmer(ABC):
    """Abstract stemmer interface."""

    @abstractmethod
    def stem(self, word: str) -> str:
        """Return the stem of *word*."""


class PorterStemmer(Stemmer):
    """Wrapper around NLTK's Porter stemmer."""

    def __init__(self) -> None:
        from nltk.stem import PorterStemmer as _PorterStemmer  # type: ignore[import-untyped]
        self._stemmer = _PorterStemmer()

    @lru_cache(maxsize=10_000)
    def stem(self, word: str) -> str:
        return self._stemmer.stem(word)


class SnowballStemmer(Stemmer):
    """Wrapper around NLTK's Snowball stemmer for English."""

    def __init__(self) -> None:
        from nltk.stem import SnowballStemmer as _SnowballStemmer  # type: ignore[import-untyped]
        self._stemmer = _SnowballStemmer("english")

    @lru_cache(maxsize=10_000)
    def stem(self, word: str) -> str:
        return self._stemmer.stem(word)


class StemExtractor:
    """High-level API for stem extraction.

    Args:
        algorithm: ``'porter'`` or ``'snowball'`` (default).
    """

    def __init__(self, algorithm: str = "snowball") -> None:
        self._stemmer: Stemmer
        if algorithm == "porter":
            self._stemmer = PorterStemmer()
        else:
            self._stemmer = SnowballStemmer()
        self._algorithm = algorithm
        logger.debug("StemExtractor initialized with %s algorithm", algorithm)

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
