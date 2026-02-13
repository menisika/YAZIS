"""Abstract repository interface for dictionary persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from models.dictionary import Dictionary


class DictionaryRepository(ABC):
    """Abstract base for dictionary storage backends.

    Implementations must provide save/load semantics for the
    :class:`~models.dictionary.Dictionary` aggregate.
    """

    @abstractmethod
    def save(self, dictionary: Dictionary, path: Path) -> None:
        """Persist a dictionary to the given path.

        Args:
            dictionary: The dictionary to save.
            path: File/database path to write to.

        Raises:
            StorageError: On I/O failures.
        """

    @abstractmethod
    def load(self, path: Path) -> Dictionary:
        """Load a dictionary from the given path.

        Args:
            path: File/database path to read from.

        Returns:
            The loaded dictionary.

        Raises:
            StorageError: On I/O failures or missing file.
            SerializationError: On data format errors.
        """

    @abstractmethod
    def exists(self, path: Path) -> bool:
        """Check whether a persisted dictionary exists at *path*."""
