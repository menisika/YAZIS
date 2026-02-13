"""Custom exception hierarchy for the application."""


class YazisError(Exception):
    """Base exception for all YAZIS errors."""


# --- Document Processing Errors ---

class DocumentError(YazisError):
    """Base for document processing errors."""


class UnsupportedFormatError(DocumentError):
    """Raised when a file format is not supported."""

    def __init__(self, path: str, fmt: str | None = None) -> None:
        self.path = path
        self.fmt = fmt
        msg = f"Unsupported file format: {fmt or path}"
        super().__init__(msg)


class DocumentParsingError(DocumentError):
    """Raised when a document cannot be parsed."""

    def __init__(self, path: str, reason: str = "") -> None:
        self.path = path
        msg = f"Failed to parse document '{path}'"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


# --- Analysis Errors ---

class AnalysisError(YazisError):
    """Base for NLP analysis errors."""


class TokenizationError(AnalysisError):
    """Raised when tokenization fails."""


class MorphologyError(AnalysisError):
    """Raised when morphological analysis fails."""


# --- Dictionary Errors ---

class DictionaryError(YazisError):
    """Base for dictionary management errors."""


class EntryNotFoundError(DictionaryError):
    """Raised when a dictionary entry is not found."""

    def __init__(self, lexeme: str) -> None:
        self.lexeme = lexeme
        super().__init__(f"Entry not found: '{lexeme}'")


class DuplicateEntryError(DictionaryError):
    """Raised when attempting to add a duplicate entry."""

    def __init__(self, lexeme: str) -> None:
        self.lexeme = lexeme
        super().__init__(f"Entry already exists: '{lexeme}'")


# --- Persistence Errors ---

class PersistenceError(YazisError):
    """Base for data persistence errors."""


class SerializationError(PersistenceError):
    """Raised when serialization/deserialization fails."""


class StorageError(PersistenceError):
    """Raised for file I/O or database errors."""


# --- Configuration Errors ---

class ConfigurationError(YazisError):
    """Raised for configuration loading/validation errors."""


# --- Export Errors ---

class ExportError(YazisError):
    """Raised when export fails."""

    def __init__(self, fmt: str, reason: str = "") -> None:
        self.fmt = fmt
        msg = f"Export to {fmt} failed"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
