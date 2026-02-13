"""Study manager: study list CRUD, progress tracking, card selection."""

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
    """Manages the study list, progress records, and card selection.

    Persists progress to ``~/.yazis/study_progress.json``.

    Args:
        path: Override the default progress file path.
    """

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or STUDY_PROGRESS_PATH
        self._progress = StudyProgress.load(self._path)

    @property
    def progress(self) -> StudyProgress:
        return self._progress

    # --- Study list CRUD ---

    def add_to_study_list(self, lexeme: str) -> None:
        """Add a word to the study list."""
        rec = self._progress.get_or_create(lexeme)
        rec.in_study_list = True
        self.save()
        logger.debug("Added '%s' to study list", lexeme)

    def remove_from_study_list(self, lexeme: str) -> None:
        """Remove a word from the study list."""
        rec = self._progress.get_or_create(lexeme)
        rec.in_study_list = False
        self.save()
        logger.debug("Removed '%s' from study list", lexeme)

    def is_in_study_list(self, lexeme: str) -> bool:
        key = lexeme.lower()
        rec = self._progress.records.get(key)
        return rec.in_study_list if rec else False

    def get_study_list(self) -> list[str]:
        """Return all lexemes in the study list."""
        return [
            rec.lexeme
            for rec in self._progress.records.values()
            if rec.in_study_list
        ]

    # --- Recording results ---

    def record_result(self, lexeme: str, known: bool) -> None:
        """Record a study attempt result.

        Args:
            lexeme: The word studied.
            known: ``True`` if user marked "I know this".
        """
        rec = self._progress.get_or_create(lexeme)
        if known:
            rec.known_count += 1
        else:
            rec.practice_count += 1
        rec.last_studied = datetime.now(timezone.utc).isoformat()
        self.save()

    # --- Card selection ---

    def select_cards(
        self,
        entries: list[DictionaryEntry],
        count: int = DEFAULT_CARDS_PER_SESSION,
        mode: str = "word_to_def",
    ) -> list[DictionaryEntry]:
        """Select cards for a study session with priority ordering.

        Priority groups (highest first):
        1. Words in study list
        2. Words with high practice_count / low known_count (needs work)
        3. Never-studied words
        4. Well-known words

        Within each group, entries are shuffled randomly.

        Args:
            entries: Available dictionary entries.
            count: Maximum number of cards to select.
            mode: Study mode (``word_to_def``, ``def_to_word``, ``word_form_practice``).
                  For ``word_to_def`` / ``def_to_word``, entries without
                  definitions are deprioritized.

        Returns:
            Ordered list of entries for the session.
        """
        needs_def = mode in ("word_to_def", "def_to_word")

        # Partition into priority groups
        study_list: list[DictionaryEntry] = []
        needs_practice: list[DictionaryEntry] = []
        never_studied: list[DictionaryEntry] = []
        well_known: list[DictionaryEntry] = []

        for entry in entries:
            # Skip entries without definitions in definition-based modes
            if needs_def and not entry.definition:
                continue

            rec = self._progress.records.get(entry.lexeme.lower())

            if rec and rec.in_study_list:
                study_list.append(entry)
            elif rec and rec.total_attempts > 0:
                if rec.score < 0.7:
                    needs_practice.append(entry)
                else:
                    well_known.append(entry)
            else:
                never_studied.append(entry)

        # Shuffle within groups
        for group in (study_list, needs_practice, never_studied, well_known):
            random.shuffle(group)

        # Concatenate in priority order and take first `count`
        ordered = study_list + needs_practice + never_studied + well_known
        selected = ordered[:count]

        logger.info(
            "Selected %d cards (mode=%s): %d study-list, %d needs-practice, "
            "%d never-studied, %d well-known",
            len(selected), mode, len(study_list), len(needs_practice),
            len(never_studied), len(well_known),
        )
        return selected

    # --- Persistence ---

    def save(self) -> None:
        """Persist progress to disk."""
        self._progress.save(self._path)

    def reload(self) -> None:
        """Reload progress from disk."""
        self._progress = StudyProgress.load(self._path)
