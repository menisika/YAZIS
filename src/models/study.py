"""Study progress models for the flashcard system."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from utils.logging_config import get_logger

logger = get_logger("models.study")


@dataclass
class StudyRecord:
    """Tracks study progress for a single lexeme.

    Attributes:
        lexeme: The word being studied.
        known_count: Times the user marked "I know this".
        practice_count: Times the user marked "Need practice".
        last_studied: ISO-8601 timestamp of last study.
        in_study_list: Whether user explicitly added this to study list.
    """

    lexeme: str
    known_count: int = 0
    practice_count: int = 0
    last_studied: str = ""
    in_study_list: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "lexeme": self.lexeme,
            "known_count": self.known_count,
            "practice_count": self.practice_count,
            "last_studied": self.last_studied,
            "in_study_list": self.in_study_list,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StudyRecord:
        return cls(
            lexeme=data["lexeme"],
            known_count=data.get("known_count", 0),
            practice_count=data.get("practice_count", 0),
            last_studied=data.get("last_studied", ""),
            in_study_list=data.get("in_study_list", False),
        )

    @property
    def total_attempts(self) -> int:
        return self.known_count + self.practice_count

    @property
    def score(self) -> float:
        """Score between 0.0 (needs practice) and 1.0 (well known)."""
        if self.total_attempts == 0:
            return 0.0
        return self.known_count / self.total_attempts


@dataclass
class StudyProgress:
    """Aggregation of all study records, with JSON persistence.

    Attributes:
        records: Mapping from lowercase lexeme to :class:`StudyRecord`.
    """

    records: dict[str, StudyRecord] = field(default_factory=dict)

    def get_or_create(self, lexeme: str) -> StudyRecord:
        """Get the record for *lexeme*, creating one if absent."""
        key = lexeme.lower()
        if key not in self.records:
            self.records[key] = StudyRecord(lexeme=lexeme)
        return self.records[key]

    def to_dict(self) -> dict[str, Any]:
        return {
            "records": {k: v.to_dict() for k, v in self.records.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StudyProgress:
        records = {}
        for key, rec_data in data.get("records", {}).items():
            records[key] = StudyRecord.from_dict(rec_data)
        return cls(records=records)

    def save(self, path: Path) -> None:
        """Persist to a JSON file."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(self.to_dict(), fh, ensure_ascii=False, indent=2)
            logger.debug("Study progress saved to %s", path)
        except OSError as exc:
            logger.warning("Failed to save study progress: %s", exc)

    @classmethod
    def load(cls, path: Path) -> StudyProgress:
        """Load from a JSON file, returning empty progress if missing."""
        if not path.exists():
            return cls()
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            progress = cls.from_dict(data)
            logger.debug("Study progress loaded from %s (%d records)", path, len(progress.records))
            return progress
        except (OSError, json.JSONDecodeError, KeyError) as exc:
            logger.warning("Failed to load study progress from %s: %s", path, exc)
            return cls()
