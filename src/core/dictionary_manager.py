"""Dictionary manager: Singleton, CRUD, Observer (Qt signals), undo/redo."""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QObject, pyqtSignal

from data.repository import DictionaryRepository
from models.dictionary import Dictionary, DictionaryMetadata
from models.lexeme import DictionaryEntry
from utils.exceptions import EntryNotFoundError
from utils.logging_config import get_logger

logger = get_logger("core.dictionary_manager")


# --- Command pattern for undo/redo ---


class Command(ABC):
    """Abstract command for undo/redo."""

    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""

    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""


class AddEntryCommand(Command):
    def __init__(self, dictionary: Dictionary, entry: DictionaryEntry) -> None:
        self._dict = dictionary
        self._entry = entry

    def execute(self) -> None:
        self._dict.add_entry(self._entry)

    def undo(self) -> None:
        self._dict.remove_entry(self._entry.lexeme)


class RemoveEntryCommand(Command):
    def __init__(self, dictionary: Dictionary, lexeme: str) -> None:
        self._dict = dictionary
        self._lexeme = lexeme
        self._removed_entry: DictionaryEntry | None = None

    def execute(self) -> None:
        self._removed_entry = self._dict.remove_entry(self._lexeme)

    def undo(self) -> None:
        if self._removed_entry:
            self._dict.add_entry(self._removed_entry)


class UpdateEntryCommand(Command):
    def __init__(self, dictionary: Dictionary, new_entry: DictionaryEntry) -> None:
        self._dict = dictionary
        self._new_entry = new_entry
        self._old_entry: DictionaryEntry | None = None

    def execute(self) -> None:
        existing = self._dict.get_entry(self._new_entry.lexeme)
        self._old_entry = deepcopy(existing) if existing else None
        self._dict.update_entry(self._new_entry)

    def undo(self) -> None:
        if self._old_entry:
            self._dict.update_entry(self._old_entry)
        else:
            self._dict.remove_entry(self._new_entry.lexeme)


class DictionaryManager(QObject):
    """
    Singleton manager for dictionary CRUD with observer signals.

    Signals:
        dictionary_changed: Emitted when the dictionary content changes.
        entry_selected: Emitted when an entry is selected in the UI.
        dictionary_loaded: Emitted when a dictionary is loaded from disk.
        dictionary_saved: Emitted when a dictionary is saved to disk.
    """

    # Qt signals for Observer pattern
    dictionary_changed = pyqtSignal()
    entry_selected = pyqtSignal(object)  # DictionaryEntry or None
    dictionary_loaded = pyqtSignal()
    dictionary_saved = pyqtSignal()

    _instance: DictionaryManager | None = None

    def __init__(self, repository: DictionaryRepository | None = None) -> None:
        super().__init__()
        self._dictionary = Dictionary(
            metadata=DictionaryMetadata(
                created=datetime.now(UTC).isoformat(),
            ),
        )
        self._repository = repository
        self._undo_stack: list[Command] = []
        self._redo_stack: list[Command] = []
        self._current_path: Path | None = None
        self._dirty = False

    @classmethod
    def get_instance(
        cls, repository: DictionaryRepository | None = None
    ) -> DictionaryManager:
        """Return the singleton instance, creating it on first call.

        Args:
            repository: Storage backend (only used on first call).
        """
        if cls._instance is None:
            cls._instance = cls(repository=repository)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton for testing."""
        cls._instance = None

    # --- Properties ---

    @property
    def dictionary(self) -> Dictionary:
        return self._dictionary

    @property
    def repository(self) -> DictionaryRepository | None:
        return self._repository

    @repository.setter
    def repository(self, repo: DictionaryRepository) -> None:
        self._repository = repo

    @property
    def current_path(self) -> Path | None:
        return self._current_path

    @property
    def is_dirty(self) -> bool:
        return self._dirty

    @property
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    # --- CRUD operations ---

    def add_entry(self, entry: DictionaryEntry) -> None:
        """Add an entry (with undo support)."""
        cmd = AddEntryCommand(self._dictionary, entry)
        self._execute_command(cmd)
        logger.info("Added entry: %s", entry.lexeme)

    def remove_entry(self, lexeme: str) -> None:
        """Remove an entry by lexeme (with undo support)."""
        if not self._dictionary.has_entry(lexeme):
            raise EntryNotFoundError(lexeme)
        cmd = RemoveEntryCommand(self._dictionary, lexeme)
        self._execute_command(cmd)
        logger.info("Removed entry: %s", lexeme)

    def update_entry(self, entry: DictionaryEntry) -> None:
        """Update an existing entry (with undo support)."""
        cmd = UpdateEntryCommand(self._dictionary, entry)
        self._execute_command(cmd)
        logger.info("Updated entry: %s", entry.lexeme)

    def get_entry(self, lexeme: str) -> DictionaryEntry | None:
        return self._dictionary.get_entry(lexeme)

    def bulk_add(self, entries: list[DictionaryEntry]) -> None:
        """Add many entries at once (single undo point not supported; marks dirty)."""
        for entry in entries:
            self._dictionary.add_entry(entry)
        self._dirty = True
        self._undo_stack.clear()
        self._redo_stack.clear()
        self.dictionary_changed.emit()
        logger.info("Bulk-added %d entries", len(entries))

    # --- Undo / Redo ---

    def undo(self) -> None:
        if not self._undo_stack:
            return
        cmd = self._undo_stack.pop()
        cmd.undo()
        self._redo_stack.append(cmd)
        self._dirty = True
        self.dictionary_changed.emit()
        logger.debug("Undo executed")

    def redo(self) -> None:
        if not self._redo_stack:
            return
        cmd = self._redo_stack.pop()
        cmd.execute()
        self._undo_stack.append(cmd)
        self._dirty = True
        self.dictionary_changed.emit()
        logger.debug("Redo executed")

    # --- Persistence ---

    def save(self, path: Path | None = None) -> None:
        """Save dictionary to disk."""
        if self._repository is None:
            raise RuntimeError("No repository configured")
        save_path = path or self._current_path
        if save_path is None:
            raise RuntimeError("No save path specified")

        self._dictionary.metadata.touch()
        self._repository.save(self._dictionary, save_path)
        self._current_path = save_path
        self._dirty = False
        self.dictionary_saved.emit()
        logger.info("Dictionary saved to %s", save_path)

    def load(self, path: Path) -> None:
        """Load dictionary from disk."""
        if self._repository is None:
            raise RuntimeError("No repository configured")

        self._dictionary = self._repository.load(path)
        self._current_path = path
        self._dirty = False
        self._undo_stack.clear()
        self._redo_stack.clear()
        self.dictionary_loaded.emit()
        self.dictionary_changed.emit()
        logger.info("Dictionary loaded from %s", path)

    def new_dictionary(self) -> None:
        """Create a fresh, empty dictionary."""
        self._dictionary = Dictionary(
            metadata=DictionaryMetadata(
                created=datetime.now(UTC).isoformat(),
            ),
        )
        self._current_path = None
        self._dirty = False
        self._undo_stack.clear()
        self._redo_stack.clear()
        self.dictionary_loaded.emit()
        self.dictionary_changed.emit()
        logger.info("New empty dictionary created")

    # --- Internal ---

    def _execute_command(self, cmd: Command) -> None:
        cmd.execute()
        self._undo_stack.append(cmd)
        self._redo_stack.clear()
        self._dirty = True
        self.dictionary_changed.emit()
