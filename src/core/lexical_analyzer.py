"""Лексический анализ: токенизация, лемматизация и подсчёт частот."""

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

# Отложенная инициализация: соответствие Penn Treebank POS -> WordNet POS
_WN_POS_MAP: dict[str, str] | None = None


def _get_wn_pos_map() -> dict[str, str]:
    """Построить при первом обращении соответствие Penn -> WordNet POS."""
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

# Токены для игнорирования (пунктуация, только цифры, один символ)
_SKIP_PATTERN = re.compile(r"^[\W\d_]+$|^.$")


class LexicalAnalyzer:
    """Токенизация текста, извлечение уникальных лемм и подсчёт частот.

    Использует NLTK word_tokenize для токенизации и WordNetLemmatizer для лемматизации.
    """

    def __init__(self) -> None:
        self._lemmatizer = WordNetLemmatizer()

    def tokenize(self, text: str) -> list[str]:
        """Разбить текст на токены в нижнем регистре.

        Аргументы:
            text: Входной текст.

        Возвращает:
            Список токенов в нижнем регистре без пунктуации.
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
        """Присвоить частеречные теги списку токенов (NLTK averaged perceptron).

        Аргументы:
            tokens: Список токенов.

        Возвращает:
            Список пар (токен, POS_тег).
        """
        return nltk.pos_tag(tokens)

    @lru_cache(maxsize=10_000)
    def lemmatize(self, word: str, penn_tag: str = "NN") -> str:
        """Лемматизировать слово по тегу Penn Treebank.

        Аргументы:
            word: Слово в нижнем регистре.
            penn_tag: POS-тег Penn Treebank.

        Возвращает:
            Лемма (базовая форма).
        """
        pos_map = _get_wn_pos_map()
        wn_pos = pos_map.get(penn_tag[0], "n")
        return self._lemmatizer.lemmatize(word, pos=wn_pos)

    def extract_lexemes(
        self, text: str
    ) -> tuple[dict[str, int], dict[str, PartOfSpeech], dict[str, list[str]]]:
        """Полный пайплайн извлечения лексем.

        Аргументы:
            text: Исходный текст документа.

        Возвращает:
            Кортеж: (freq — {лемма: частота}, pos_map — {лемма: PartOfSpeech},
            forms_map — {лемма: [исходные_токены]}).
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

        # Выбрать наиболее частую часть речи для каждой леммы
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
