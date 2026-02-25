"""Иерархия пользовательских исключений приложения."""


class YazisError(Exception):
    """Базовое исключение для всех ошибок YAZIS."""


# Ошибки обработки документов

class DocumentError(YazisError):
    """Базовый класс ошибок обработки документов."""


class UnsupportedFormatError(DocumentError):
    """Вызывается при неподдерживаемом формате файла."""

    def __init__(self, path: str, fmt: str | None = None) -> None:
        self.path = path
        self.fmt = fmt
        msg = f"Unsupported file format: {fmt or path}"
        super().__init__(msg)


class DocumentParsingError(DocumentError):
    """Вызывается при невозможности разобрать документ."""

    def __init__(self, path: str, reason: str = "") -> None:
        self.path = path
        msg = f"Failed to parse document '{path}'"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


# Ошибки анализа

class AnalysisError(YazisError):
    """Базовый класс ошибок NLP-анализа."""


class TokenizationError(AnalysisError):
    """Вызывается при сбое токенизации."""


class MorphologyError(AnalysisError):
    """Вызывается при сбое морфологического анализа."""


# Ошибки словаря

class DictionaryError(YazisError):
    """Базовый класс ошибок управления словарём."""


class EntryNotFoundError(DictionaryError):
    """Вызывается, когда запись словаря не найдена."""

    def __init__(self, lexeme: str) -> None:
        self.lexeme = lexeme
        super().__init__(f"Entry not found: '{lexeme}'")


class DuplicateEntryError(DictionaryError):
    """Вызывается при попытке добавить дубликат записи."""

    def __init__(self, lexeme: str) -> None:
        self.lexeme = lexeme
        super().__init__(f"Entry already exists: '{lexeme}'")


# Ошибки сохранения

class PersistenceError(YazisError):
    """Базовый класс ошибок сохранения данных."""


class SerializationError(PersistenceError):
    """Вызывается при сбое сериализации/десериализации."""


class StorageError(PersistenceError):
    """Вызывается при ошибках файлового ввода-вывода или БД."""


# Ошибки конфигурации

class ConfigurationError(YazisError):
    """Вызывается при ошибках загрузки или проверки конфигурации."""


# Ошибки экспорта

class ExportError(YazisError):
    """Вызывается при сбое экспорта."""

    def __init__(self, fmt: str, reason: str = "") -> None:
        self.fmt = fmt
        msg = f"Export to {fmt} failed"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
