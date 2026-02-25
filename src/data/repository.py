"""Абстрактный интерфейс репозитория для сохранения словаря."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from models.dictionary import Dictionary


class DictionaryRepository(ABC):
    """Абстрактная база для бэкендов хранения словаря.

    Реализации должны обеспечивать семантику save/load для агрегата Dictionary.
    """

    @abstractmethod
    def save(self, dictionary: Dictionary, path: Path) -> None:
        """Сохранить словарь по заданному пути.

        Аргументы:
            dictionary: Словарь для сохранения.
            path: Путь к файлу или БД.

        Исключения:
            StorageError: при ошибках ввода-вывода.
        """

    @abstractmethod
    def load(self, path: Path) -> Dictionary:
        """Загрузить словарь по заданному пути.

        Аргументы:
            path: Путь к файлу или БД.

        Возвращает:
            Загруженный словарь.

        Исключения:
            StorageError: при ошибках ввода-вывода или отсутствии файла.
            SerializationError: при ошибках формата данных.
        """

    @abstractmethod
    def exists(self, path: Path) -> bool:
        """Проверить, существует ли сохранённый словарь по path."""
