"""Export service with Strategy pattern for JSON/CSV/TXT formats."""

from __future__ import annotations

import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from models.lexeme import DictionaryEntry
from utils.exceptions import ExportError
from utils.logging_config import get_logger

logger = get_logger("core.export_service")


class ExportStrategy(ABC):
    """Abstract export strategy."""

    @abstractmethod
    def export(self, entries: list[DictionaryEntry], path: Path) -> None:
        """Export entries to the specified path.

        Args:
            entries: Dictionary entries to export.
            path: Output file path.

        Raises:
            ExportError: On write failures.
        """

    @abstractmethod
    def file_extension(self) -> str:
        """Default file extension for this format (e.g. ``'.json'``)."""


class JSONExporter(ExportStrategy):
    """Export dictionary entries as a JSON array."""

    def export(self, entries: list[DictionaryEntry], path: Path) -> None:
        try:
            data = [e.to_dict() for e in entries]
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
            logger.info("Exported %d entries to JSON: %s", len(entries), path)
        except (OSError, TypeError, ValueError) as exc:
            raise ExportError("JSON", str(exc)) from exc

    def file_extension(self) -> str:
        return ".json"


class CSVExporter(ExportStrategy):
    """Export dictionary entries as a flat CSV.

    Columns: lexeme, stem, pos, frequency, irregular, word_forms (semicolon-separated), notes
    """

    def export(self, entries: list[DictionaryEntry], path: Path) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="") as fh:
                writer = csv.writer(fh)
                writer.writerow([
                    "lexeme", "stem", "pos", "frequency", "irregular",
                    "word_forms", "notes",
                ])
                for entry in entries:
                    forms_str = "; ".join(
                        f"{wf.form} ({wf.features.summary()})"
                        for wf in entry.word_forms
                    )
                    writer.writerow([
                        entry.lexeme,
                        entry.stem,
                        str(entry.pos),
                        entry.frequency,
                        entry.irregular,
                        forms_str,
                        entry.notes,
                    ])
            logger.info("Exported %d entries to CSV: %s", len(entries), path)
        except OSError as exc:
            raise ExportError("CSV", str(exc)) from exc

    def file_extension(self) -> str:
        return ".csv"


class TXTExporter(ExportStrategy):
    """Export dictionary entries as human-readable plain text."""

    def export(self, entries: list[DictionaryEntry], path: Path) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(f"Dictionary Export ({len(entries)} entries)\n")
                fh.write("=" * 60 + "\n\n")

                for entry in entries:
                    fh.write(f"--- {entry.lexeme} ---\n")
                    fh.write(f"  POS:       {entry.pos}\n")
                    fh.write(f"  Stem:      {entry.stem}\n")
                    fh.write(f"  Frequency: {entry.frequency}\n")
                    fh.write(f"  Irregular: {'Yes' if entry.irregular else 'No'}\n")
                    if entry.word_forms:
                        fh.write("  Forms:\n")
                        for wf in entry.word_forms:
                            fh.write(f"    {wf.form:20s} [{wf.ending:8s}]  {wf.features.summary()}\n")
                    if entry.notes:
                        fh.write(f"  Notes: {entry.notes}\n")
                    fh.write("\n")

            logger.info("Exported %d entries to TXT: %s", len(entries), path)
        except OSError as exc:
            raise ExportError("TXT", str(exc)) from exc

    def file_extension(self) -> str:
        return ".txt"


class ExportService:
    """Facade that dispatches export to the correct strategy.

    Strategies are registered by format key.
    """

    def __init__(self) -> None:
        self._strategies: dict[str, ExportStrategy] = {
            "json": JSONExporter(),
            "csv": CSVExporter(),
            "txt": TXTExporter(),
        }

    def register_strategy(self, key: str, strategy: ExportStrategy) -> None:
        """Register a custom export strategy."""
        self._strategies[key.lower()] = strategy

    @property
    def available_formats(self) -> list[str]:
        return list(self._strategies.keys())

    def export(
        self,
        entries: list[DictionaryEntry],
        path: Path,
        fmt: str = "json",
    ) -> None:
        """Export entries to the given format and path.

        Args:
            entries: Entries to export.
            path: Output file path.
            fmt: Format key (``json``, ``csv``, ``txt``).

        Raises:
            ExportError: If format is unknown or export fails.
        """
        strategy = self._strategies.get(fmt.lower())
        if strategy is None:
            raise ExportError(fmt, f"Unknown export format: {fmt}")
        strategy.export(entries, path)

    def get_extension(self, fmt: str) -> str:
        """Get the file extension for a format."""
        strategy = self._strategies.get(fmt.lower())
        return strategy.file_extension() if strategy else ".txt"
