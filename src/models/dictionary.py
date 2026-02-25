"""Агрегат словаря: метаданные и записи."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from models.lexeme import DictionaryEntry


@dataclass(slots=True)
class DictionaryMetadata:
    """Метаданные сохранённого словаря.

    Атрибуты:
        created: Время создания (ISO-8601).
        modified: Время последнего изменения (ISO-8601).
        language: Язык словаря.
        total_lexemes: Количество записей (кэш).
        source_documents: Список имён исходных документов.
    """

    created: str = ""
    modified: str = ""
    language: str = "English"
    total_lexemes: int = 0
    source_documents: list[str] = field(default_factory=list)

    def touch(self) -> None:
        """Обновить время последнего изменения на текущее."""
        self.modified = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "created": self.created,
            "modified": self.modified,
            "language": self.language,
            "total_lexemes": self.total_lexemes,
            "source_documents": list(self.source_documents),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DictionaryMetadata:
        return cls(
            created=data.get("created", ""),
            modified=data.get("modified", ""),
            language=data.get("language", "English"),
            total_lexemes=data.get("total_lexemes", 0),
            source_documents=data.get("source_documents", []),
        )


@dataclass
class Dictionary:
    """Корневой агрегат словаря.

    Хранит индексированную коллекцию DictionaryEntry.
    Поиск по лексеме за O(1) через внутренний словарь.

    Атрибуты:
        metadata: Метаданные словаря.
        _entries: Внутренний словарь: лексема (нижний регистр) -> запись.
    """

    metadata: DictionaryMetadata = field(default_factory=DictionaryMetadata)
    _entries: dict[str, DictionaryEntry] = field(default_factory=dict)

    # CRUD

    def add_entry(self, entry: DictionaryEntry) -> None:
        """Добавить или слить запись. При существовании объединяет словоформы."""
        key = entry.lexeme.lower()
        if key in self._entries:
            existing = self._entries[key]
            existing.frequency += entry.frequency
            for wf in entry.word_forms:
                existing.add_word_form(wf)
        else:
            self._entries[key] = entry
        self._sync_count()

    def get_entry(self, lexeme: str) -> DictionaryEntry | None:
        """Поиск по лексеме за O(1)."""
        return self._entries.get(lexeme.lower())

    def remove_entry(self, lexeme: str) -> DictionaryEntry | None:
        """Удалить и вернуть запись или None, если не найдена."""
        entry = self._entries.pop(lexeme.lower(), None)
        if entry is not None:
            self._sync_count()
        return entry

    def update_entry(self, entry: DictionaryEntry) -> None:
        """Заменить существующую запись целиком."""
        self._entries[entry.lexeme.lower()] = entry
        self._sync_count()

    def has_entry(self, lexeme: str) -> bool:
        return lexeme.lower() in self._entries

    # Итерация и массовые операции

    @property
    def entries(self) -> list[DictionaryEntry]:
        """Все записи, отсортированные по алфавиту."""
        return sorted(self._entries.values(), key=lambda e: e.lexeme.lower())

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(self.entries)

    def clear(self) -> None:
        """Удалить все записи."""
        self._entries.clear()
        self._sync_count()

    # Сериализация

    def to_dict(self) -> dict[str, Any]:
        self._sync_count()
        return {
            "metadata": self.metadata.to_dict(),
            "entries": [e.to_dict() for e in self.entries],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Dictionary:
        meta = DictionaryMetadata.from_dict(data.get("metadata", {}))
        d = cls(metadata=meta)
        for entry_data in data.get("entries", []):
            entry = DictionaryEntry.from_dict(entry_data)
            d._entries[entry.lexeme.lower()] = entry
        d._sync_count()
        return d

    # Внутренние методы

    def _sync_count(self) -> None:
        self.metadata.total_lexemes = len(self._entries)
