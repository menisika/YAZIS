"""Движок поиска и фильтрации записей словаря."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field

from models.dictionary import Dictionary
from models.enums import PartOfSpeech
from models.lexeme import DictionaryEntry
from utils.constants import DEFAULT_PAGE_SIZE
from utils.logging_config import get_logger

logger = get_logger("core.search_engine")


@dataclass(slots=True)
class SearchCriteria:
    """Параметры фильтрации записей словаря.

    Атрибуты:
        query: Текстовый запрос (поддержка масок * и ?).
        pos_filter: Фильтр по части речи (None — любая).
        min_frequency: Минимальная частота.
        max_frequency: Максимальная частота (0 — без ограничения).
        stem_contains: Фильтр по вхождению подстроки в основу.
        has_ending: Фильтр по окончанию.
        use_regex: Если True, считать query регулярным выражением.
    """

    query: str = ""
    pos_filter: PartOfSpeech | None = None
    min_frequency: int = 0
    max_frequency: int = 0
    stem_contains: str = ""
    has_ending: str = ""
    use_regex: bool = False


@dataclass(slots=True)
class SearchResult:
    """Результат поиска с постраничной разбивкой.

    Атрибуты:
        entries: Совпадающие записи на текущей странице.
        total_count: Общее число совпадений.
        page: Номер текущей страницы (начиная с 1).
        page_size: Записей на странице.
        total_pages: Всего страниц.
    """

    entries: list[DictionaryEntry] = field(default_factory=list)
    total_count: int = 0
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE
    total_pages: int = 1


class SearchEngine:
    """Фильтрация и поиск записей словаря с постраничной разбивкой."""

    def search(
        self,
        dictionary: Dictionary,
        criteria: SearchCriteria,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
        sort_by: str = "lexeme",
        ascending: bool = True,
    ) -> SearchResult:
        """Выполнить поиск по словарю.

        Аргументы:
            dictionary: Словарь для поиска.
            criteria: Критерии фильтрации.
            page: Номер страницы (с 1).
            page_size: Записей на странице.
            sort_by: Ключ сортировки (lexeme, pos, stem, frequency).
            ascending: Направление сортировки.

        Возвращает:
            SearchResult с совпадающими записями.
        """
        matches = self._filter(dictionary, criteria)
        matches = self._sort(matches, sort_by, ascending)

        total = len(matches)
        total_pages = max(1, (total + page_size - 1) // page_size)
        page = max(1, min(page, total_pages))
        start = (page - 1) * page_size
        end = start + page_size

        result = SearchResult(
            entries=matches[start:end],
            total_count=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
        logger.debug(
            "Search returned %d/%d entries (page %d/%d)",
            len(result.entries), total, page, total_pages,
        )
        return result

    def _filter(
        self, dictionary: Dictionary, criteria: SearchCriteria
    ) -> list[DictionaryEntry]:
        """Применить все критерии фильтрации."""
        entries = dictionary.entries  # уже отсортированы по алфавиту

        if criteria.query:
            entries = self._filter_by_query(entries, criteria.query, criteria.use_regex)

        if criteria.pos_filter is not None:
            entries = [e for e in entries if e.pos == criteria.pos_filter]

        if criteria.min_frequency > 0:
            entries = [e for e in entries if e.frequency >= criteria.min_frequency]

        if criteria.max_frequency > 0:
            entries = [e for e in entries if e.frequency <= criteria.max_frequency]

        if criteria.stem_contains:
            sub = criteria.stem_contains.lower()
            entries = [e for e in entries if sub in e.stem.lower()]

        if criteria.has_ending:
            ending = criteria.has_ending.lower()
            entries = [
                e for e in entries
                if any(ending in wf.ending.lower() for wf in e.word_forms)
            ]

        return entries

    @staticmethod
    def _filter_by_query(
        entries: list[DictionaryEntry], query: str, use_regex: bool
    ) -> list[DictionaryEntry]:
        """Фильтровать записи по шаблону лексемы."""
        query = query.strip()
        if not query:
            return entries

        if use_regex:
            try:
                pattern = re.compile(query, re.IGNORECASE)
            except re.error:
                logger.warning("Invalid regex pattern: %s", query)
                return entries
            return [e for e in entries if pattern.search(e.lexeme)]
        else:
            # Сопоставление по маскам
            query_lower = query.lower()
            if "*" in query or "?" in query:
                return [e for e in entries if fnmatch.fnmatch(e.lexeme.lower(), query_lower)]
            else:
                return [e for e in entries if query_lower in e.lexeme.lower()]

    @staticmethod
    def _sort(
        entries: list[DictionaryEntry], sort_by: str, ascending: bool
    ) -> list[DictionaryEntry]:
        """Сортировать записи по заданному ключу."""
        key_funcs = {
            "lexeme": lambda e: e.lexeme.lower(),
            "pos": lambda e: e.pos.display_name(),
            "stem": lambda e: e.stem.lower(),
            "frequency": lambda e: e.frequency,
        }
        key_fn = key_funcs.get(sort_by, key_funcs["lexeme"])
        return sorted(entries, key=key_fn, reverse=not ascending)
