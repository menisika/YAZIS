"""Обёртки извлечения основ (Porter / Snowball)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache

from utils.logging_config import get_logger

logger = get_logger("core.stem_extractor")


class Stemmer(ABC):
    """Абстрактный интерфейс стеммера."""

    @abstractmethod
    def stem(self, word: str) -> str:
        """Вернуть основу слова."""


class PorterStemmer(Stemmer):
    """Обёртка над стеммером Porter из NLTK."""

    def __init__(self) -> None:
        from nltk.stem import PorterStemmer as _PorterStemmer  # type: ignore[import-untyped]
        self._stemmer = _PorterStemmer()

    @lru_cache(maxsize=10_000)
    def stem(self, word: str) -> str:
        return self._stemmer.stem(word)


class SnowballStemmer(Stemmer):
    """Обёртка над стеммером Snowball (английский) из NLTK."""

    def __init__(self) -> None:
        from nltk.stem import SnowballStemmer as _SnowballStemmer  # type: ignore[import-untyped]
        self._stemmer = _SnowballStemmer("english")

    @lru_cache(maxsize=10_000)
    def stem(self, word: str) -> str:
        return self._stemmer.stem(word)


class StemExtractor:
    """Высокоуровневый API извлечения основ.

    Аргументы:
        algorithm: 'porter' или 'snowball' (по умолчанию).
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
        """Извлечь основу слова.

        Аргументы:
            word: Слово в нижнем регистре.

        Возвращает:
            Стеммированная форма.
        """
        return self._stemmer.stem(word.lower())

    def extract_batch(self, words: list[str]) -> dict[str, str]:
        """Извлечь основы для списка слов.

        Аргументы:
            words: Список слов.

        Возвращает:
            Словарь {слово: основа}.
        """
        return {w: self.extract(w) for w in words}

    @property
    def algorithm(self) -> str:
        return self._algorithm
