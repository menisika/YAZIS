"""Dictionary aggregate root holding metadata and entries."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from models.lexeme import DictionaryEntry


@dataclass(slots=True)
class DictionaryMetadata:
    """Metadata for a persisted dictionary.

    Attributes:
        created: ISO-8601 creation timestamp.
        modified: ISO-8601 last-modified timestamp.
        language: Language of the dictionary.
        total_lexemes: Number of entries (cached count).
        source_documents: List of source document filenames.
    """

    created: str = ""
    modified: str = ""
    language: str = "English"
    total_lexemes: int = 0
    source_documents: list[str] = field(default_factory=list)

    def touch(self) -> None:
        """Update the modified timestamp to now."""
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
    """The top-level dictionary aggregate.

    Holds an indexed collection of :class:`DictionaryEntry` objects.
    Provides O(1) lookup by lexeme through an internal hash map.

    Attributes:
        metadata: Dictionary-level metadata.
        _entries: Internal dict keyed by lowercase lexeme.
    """

    metadata: DictionaryMetadata = field(default_factory=DictionaryMetadata)
    _entries: dict[str, DictionaryEntry] = field(default_factory=dict)

    # --- CRUD operations ---

    def add_entry(self, entry: DictionaryEntry) -> None:
        """Add or merge an entry. Merges word forms if entry already exists."""
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
        """O(1) lookup by lexeme."""
        return self._entries.get(lexeme.lower())

    def remove_entry(self, lexeme: str) -> DictionaryEntry | None:
        """Remove and return an entry, or ``None`` if not found."""
        entry = self._entries.pop(lexeme.lower(), None)
        if entry is not None:
            self._sync_count()
        return entry

    def update_entry(self, entry: DictionaryEntry) -> None:
        """Replace an existing entry wholesale."""
        self._entries[entry.lexeme.lower()] = entry
        self._sync_count()

    def has_entry(self, lexeme: str) -> bool:
        return lexeme.lower() in self._entries

    # --- Iteration / bulk ---

    @property
    def entries(self) -> list[DictionaryEntry]:
        """All entries sorted alphabetically."""
        return sorted(self._entries.values(), key=lambda e: e.lexeme.lower())

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(self.entries)

    def clear(self) -> None:
        """Remove all entries."""
        self._entries.clear()
        self._sync_count()

    # --- Serialization ---

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

    # --- Internal ---

    def _sync_count(self) -> None:
        self.metadata.total_lexemes = len(self._entries)
