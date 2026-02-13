"""JSON file persistence adapter for Dictionary."""

from __future__ import annotations

import json
from pathlib import Path

from data.repository import DictionaryRepository
from models.dictionary import Dictionary
from utils.exceptions import SerializationError, StorageError
from utils.logging_config import get_logger

logger = get_logger("data.json")


class JSONAdapter(DictionaryRepository):
    """Persist a :class:`Dictionary` as a pretty-printed JSON file."""

    def save(self, dictionary: Dictionary, path: Path) -> None:
        """Write dictionary to *path* as JSON.

        Args:
            dictionary: Dictionary to persist.
            path: Target ``.json`` file.

        Raises:
            StorageError: On file write failures.
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            data = dictionary.to_dict()
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
            logger.info("Dictionary saved to %s (%d entries)", path, len(dictionary))
        except OSError as exc:
            raise StorageError(f"Failed to write JSON to {path}: {exc}") from exc
        except (TypeError, ValueError) as exc:
            raise SerializationError(f"Serialization error: {exc}") from exc

    def load(self, path: Path) -> Dictionary:
        """Read dictionary from a JSON file.

        Args:
            path: Source ``.json`` file.

        Returns:
            Loaded :class:`Dictionary`.

        Raises:
            StorageError: If the file does not exist or cannot be read.
            SerializationError: If the JSON is malformed.
        """
        if not path.exists():
            raise StorageError(f"File not found: {path}")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            dictionary = Dictionary.from_dict(data)
            logger.info("Dictionary loaded from %s (%d entries)", path, len(dictionary))
            return dictionary
        except OSError as exc:
            raise StorageError(f"Failed to read {path}: {exc}") from exc
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise SerializationError(f"Invalid dictionary JSON in {path}: {exc}") from exc

    def exists(self, path: Path) -> bool:
        return path.is_file()
