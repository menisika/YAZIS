"""Менеджер изучения: CRUD списка изучения, учёт прогресса, выбор карточек."""

from __future__ import annotations

import random
from datetime import datetime, timezone
from pathlib import Path

from models.lexeme import DictionaryEntry
from models.study import StudyProgress, StudyRecord
from utils.constants import DEFAULT_CARDS_PER_SESSION, STUDY_PROGRESS_PATH
from utils.logging_config import get_logger

logger = get_logger("core.study_manager")


class StudyManager:
    """Управляет списком изучения, записями прогресса и выбором карточек.

    Сохраняет прогресс в ~/.yazis/study_progress.json.

    Аргументы:
        path: Переопределить путь к файлу прогресса.
    """

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or STUDY_PROGRESS_PATH
        self._progress = StudyProgress.load(self._path)

    @property
    def progress(self) -> StudyProgress:
        return self._progress

    # CRUD списка изучения

    def add_to_study_list(self, lexeme: str) -> None:
        """Добавить слово в список изучения."""
        rec = self._progress.get_or_create(lexeme)
        rec.in_study_list = True
        self.save()
        logger.debug("Added '%s' to study list", lexeme)

    def remove_from_study_list(self, lexeme: str) -> None:
        """Удалить слово из списка изучения."""
        rec = self._progress.get_or_create(lexeme)
        rec.in_study_list = False
        self.save()
        logger.debug("Removed '%s' from study list", lexeme)

    def is_in_study_list(self, lexeme: str) -> bool:
        key = lexeme.lower()
        rec = self._progress.records.get(key)
        return rec.in_study_list if rec else False

    def get_study_list(self) -> list[str]:
        """Вернуть все лексемы из списка изучения."""
        return [
            rec.lexeme
            for rec in self._progress.records.values()
            if rec.in_study_list
        ]

    # Запись результатов

    def record_result(self, lexeme: str, known: bool) -> None:
        """Записать результат попытки изучения.

        Аргументы:
            lexeme: Изучаемое слово.
            known: True, если пользователь отметил «Знаю».
        """
        rec = self._progress.get_or_create(lexeme)
        if known:
            rec.known_count += 1
        else:
            rec.practice_count += 1
        rec.last_studied = datetime.now(timezone.utc).isoformat()
        self.save()

    # Выбор карточек

    def select_cards(
        self,
        entries: list[DictionaryEntry],
        count: int = DEFAULT_CARDS_PER_SESSION,
        mode: str = "word_to_def",
    ) -> list[DictionaryEntry]:
        """Выбрать карточки для сессии с приоритетным порядком.

        Группы приоритета (от высшего):
        1. Слова из списка изучения
        2. Слова с высоким practice_count / низким known_count (нудна практика)
        3. Никогда не изученные
        4. Хорошо изученные

        Внутри каждой группы записи перемешиваются случайно.

        Аргументы:
            entries: Доступные записи словаря.
            count: Максимальное число карточек.
            mode: Режим (word_to_def, def_to_word, word_form_practice).
                  Для word_to_def/def_to_word записи без определений
                  пропускаются, если их нет в списке изучения.

        Возвращает:
            Упорядоченный список записей для сессии.
        """
        needs_def = mode in ("word_to_def", "def_to_word")

        # Разбиение на группы по приоритету
        study_list: list[DictionaryEntry] = []
        needs_practice: list[DictionaryEntry] = []
        never_studied: list[DictionaryEntry] = []
        well_known: list[DictionaryEntry] = []

        for entry in entries:
            rec = self._progress.records.get(entry.lexeme.lower())
            # Пропуск записей без определений в режимах по определению, кроме списка изучения
            if needs_def and not entry.definition and not (rec and rec.in_study_list):
                continue

            if rec and rec.in_study_list:
                study_list.append(entry)
            elif rec and rec.total_attempts > 0:
                if rec.score < 0.7:
                    needs_practice.append(entry)
                else:
                    well_known.append(entry)
            else:
                never_studied.append(entry)

        # Перемешивание внутри групп
        for group in (study_list, needs_practice, never_studied, well_known):
            random.shuffle(group)

        # Объединение по приоритету и взятие первых count
        ordered = study_list + needs_practice + never_studied + well_known
        selected = ordered[:count]

        logger.info(
            "Selected %d cards (mode=%s): %d study-list, %d needs-practice, "
            "%d never-studied, %d well-known",
            len(selected), mode, len(study_list), len(needs_practice),
            len(never_studied), len(well_known),
        )
        return selected

    # Сохранение

    def save(self) -> None:
        """Сохранить прогресс на диск."""
        self._progress.save(self._path)

    def reload(self) -> None:
        """Перезагрузить прогресс с диска."""
        self._progress = StudyProgress.load(self._path)
