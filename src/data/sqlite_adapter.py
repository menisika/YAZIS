"""SQLite persistence adapter for Dictionary."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from data.repository import DictionaryRepository
from models.dictionary import Dictionary, DictionaryMetadata
from models.enums import PartOfSpeech
from models.lexeme import DictionaryEntry, MorphologicalFeature, WordForm
from utils.exceptions import SerializationError, StorageError
from utils.logging_config import get_logger

logger = get_logger("data.sqlite")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS metadata (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entries (
    lexeme     TEXT PRIMARY KEY,
    stem       TEXT NOT NULL,
    pos        TEXT NOT NULL,
    frequency  INTEGER NOT NULL DEFAULT 0,
    irregular  INTEGER NOT NULL DEFAULT 0,
    notes      TEXT NOT NULL DEFAULT '',
    definition TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS word_forms (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    lexeme    TEXT NOT NULL REFERENCES entries(lexeme) ON DELETE CASCADE,
    form      TEXT NOT NULL,
    ending    TEXT NOT NULL DEFAULT '',
    features  TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_wf_lexeme ON word_forms(lexeme);
"""


class SQLiteAdapter(DictionaryRepository):
    """Persist a :class:`Dictionary` in an SQLite database."""

    def save(self, dictionary: Dictionary, path: Path) -> None:
        """Write dictionary to an SQLite database at *path*.

        Replaces all existing data in the database.

        Args:
            dictionary: Dictionary to persist.
            path: Target ``.db`` file.

        Raises:
            StorageError: On database write failures.
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(path))
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")

            with conn:
                # Re-create schema (drop old data)
                conn.executescript(
                    "DROP TABLE IF EXISTS word_forms;"
                    "DROP TABLE IF EXISTS entries;"
                    "DROP TABLE IF EXISTS metadata;"
                )
                conn.executescript(_SCHEMA)

                # Metadata
                meta = dictionary.metadata
                for key, value in meta.to_dict().items():
                    conn.execute(
                        "INSERT INTO metadata (key, value) VALUES (?, ?)",
                        (key, json.dumps(value) if isinstance(value, (list, dict)) else str(value)),
                    )

                # Entries + word forms
                for entry in dictionary.entries:
                    conn.execute(
                        "INSERT INTO entries (lexeme, stem, pos, frequency, irregular, notes, definition) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (entry.lexeme, entry.stem, str(entry.pos), entry.frequency,
                         int(entry.irregular), entry.notes, entry.definition),
                    )
                    for wf in entry.word_forms:
                        conn.execute(
                            "INSERT INTO word_forms (lexeme, form, ending, features) "
                            "VALUES (?, ?, ?, ?)",
                            (entry.lexeme, wf.form, wf.ending,
                             json.dumps(wf.features.to_dict())),
                        )

            conn.close()
            logger.info("Dictionary saved to SQLite %s (%d entries)", path, len(dictionary))
        except sqlite3.Error as exc:
            raise StorageError(f"SQLite write error for {path}: {exc}") from exc

    def load(self, path: Path) -> Dictionary:
        """Load dictionary from an SQLite database.

        Args:
            path: Source ``.db`` file.

        Returns:
            Loaded :class:`Dictionary`.

        Raises:
            StorageError: If the file does not exist or cannot be read.
            SerializationError: On data format errors.
        """
        if not path.exists():
            raise StorageError(f"Database not found: {path}")
        try:
            conn = sqlite3.connect(str(path))
            conn.row_factory = sqlite3.Row

            # Load metadata
            meta_rows = conn.execute("SELECT key, value FROM metadata").fetchall()
            meta_dict: dict = {}
            for row in meta_rows:
                key, val = row["key"], row["value"]
                if key == "source_documents":
                    meta_dict[key] = json.loads(val)
                elif key == "total_lexemes":
                    meta_dict[key] = int(val)
                else:
                    meta_dict[key] = val
            metadata = DictionaryMetadata.from_dict(meta_dict)

            # Load entries
            dictionary = Dictionary(metadata=metadata)
            entry_rows = conn.execute("SELECT * FROM entries").fetchall()
            for erow in entry_rows:
                wf_rows = conn.execute(
                    "SELECT form, ending, features FROM word_forms WHERE lexeme = ?",
                    (erow["lexeme"],),
                ).fetchall()
                word_forms = [
                    WordForm(
                        form=wfr["form"],
                        ending=wfr["ending"],
                        features=MorphologicalFeature.from_dict(json.loads(wfr["features"])),
                    )
                    for wfr in wf_rows
                ]
                # 'definition' column may not exist in older databases
                defn = ""
                try:
                    defn = erow["definition"] or ""
                except (IndexError, KeyError):
                    pass
                entry = DictionaryEntry(
                    lexeme=erow["lexeme"],
                    stem=erow["stem"],
                    pos=PartOfSpeech(erow["pos"]),
                    frequency=erow["frequency"],
                    word_forms=word_forms,
                    irregular=bool(erow["irregular"]),
                    notes=erow["notes"],
                    definition=defn,
                )
                dictionary._entries[entry.lexeme.lower()] = entry

            conn.close()
            dictionary._sync_count()
            logger.info("Dictionary loaded from SQLite %s (%d entries)", path, len(dictionary))
            return dictionary
        except sqlite3.Error as exc:
            raise StorageError(f"SQLite read error for {path}: {exc}") from exc
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise SerializationError(f"Data format error in {path}: {exc}") from exc

    def exists(self, path: Path) -> bool:
        return path.is_file()
