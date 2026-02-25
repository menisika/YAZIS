"""Сервис экспорта с паттерном «Стратегия» для форматов JSON/CSV/TXT."""

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
    """Абстрактная стратегия экспорта."""

    @abstractmethod
    def export(self, entries: list[DictionaryEntry], path: Path) -> None:
        """Экспортировать записи по указанному пути.

        Аргументы:
            entries: Записи словаря для экспорта.
            path: Путь к выходному файлу.

        Исключения:
            ExportError: при ошибках записи.
        """

    @abstractmethod
    def file_extension(self) -> str:
        """Расширение по умолчанию для формата (напр. .json)."""


class JSONExporter(ExportStrategy):
    """Экспорт записей словаря в виде JSON-массива."""

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
    """Экспорт записей словаря в плоский CSV.

    Колонки: lexeme, stem, pos, frequency, irregular, word_forms (через точку с запятой), notes, definition.
    """

    def export(self, entries: list[DictionaryEntry], path: Path) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="") as fh:
                writer = csv.writer(fh)
                writer.writerow([
                    "lexeme", "stem", "pos", "frequency", "irregular",
                    "word_forms", "notes", "definition",
                ])
                for entry in entries:
                    forms_str = "; ".join(
                        f"{wf.form} ({wf.features.summary()})"
                        for wf in entry.word_forms
                    )
                    writer.writerow([
                        entry.lexeme,
                        entry.stem,
                        entry.pos.display_name(),
                        entry.frequency,
                        entry.irregular,
                        forms_str,
                        entry.notes,
                        entry.definition,
                    ])
            logger.info("Exported %d entries to CSV: %s", len(entries), path)
        except OSError as exc:
            raise ExportError("CSV", str(exc)) from exc

    def file_extension(self) -> str:
        return ".csv"


class TXTExporter(ExportStrategy):
    """Экспорт записей словаря в читаемый текстовый формат."""

    def export(self, entries: list[DictionaryEntry], path: Path) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(f"Dictionary Export ({len(entries)} entries)\n")
                fh.write("=" * 60 + "\n\n")

                for entry in entries:
                    fh.write(f"--- {entry.lexeme} ---\n")
                    fh.write(f"  POS:        {entry.pos.display_name()}\n")
                    fh.write(f"  Stem:       {entry.stem}\n")
                    fh.write(f"  Frequency:  {entry.frequency}\n")
                    fh.write(f"  Irregular:  {'Yes' if entry.irregular else 'No'}\n")
                    if entry.definition:
                        fh.write(f"  Definition: {entry.definition}\n")
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
    """Фасад: направляет экспорт в нужную стратегию.

    Стратегии регистрируются по ключу формата.
    """

    def __init__(self) -> None:
        self._strategies: dict[str, ExportStrategy] = {
            "json": JSONExporter(),
            "csv": CSVExporter(),
            "txt": TXTExporter(),
        }

    def register_strategy(self, key: str, strategy: ExportStrategy) -> None:
        """Зарегистрировать пользовательскую стратегию экспорта."""
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
        """Экспортировать записи в заданном формате по пути.

        Аргументы:
            entries: Записи для экспорта.
            path: Путь к выходному файлу.
            fmt: Ключ формата (json, csv, txt).

        Исключения:
            ExportError: при неизвестном формате или ошибке экспорта.
        """
        strategy = self._strategies.get(fmt.lower())
        if strategy is None:
            raise ExportError(fmt, f"Unknown export format: {fmt}")
        strategy.export(entries, path)

    def get_extension(self, fmt: str) -> str:
        """Получить расширение файла для формата."""
        strategy = self._strategies.get(fmt.lower())
        return strategy.file_extension() if strategy else ".txt"
