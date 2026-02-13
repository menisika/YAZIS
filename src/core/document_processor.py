"""Document processing with Factory pattern for extensibility."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from utils.exceptions import DocumentParsingError, UnsupportedFormatError
from utils.logging_config import get_logger

logger = get_logger("core.document_processor")


class DocumentProcessor(ABC):
    """Abstract base for document text extraction."""

    @abstractmethod
    def extract_text(self, path: Path) -> str:
        """Extract plain text from a document file.

        Args:
            path: Path to the document.

        Returns:
            Extracted text as a single string.

        Raises:
            DocumentParsingError: If the file cannot be parsed.
        """

    @abstractmethod
    def supported_extensions(self) -> tuple[str, ...]:
        """Return file extensions this processor handles (e.g. ``('.docx',)``)."""


class DocxProcessor(DocumentProcessor):
    """Extract text from Microsoft Word ``.docx`` files using *python-docx*."""

    def extract_text(self, path: Path) -> str:
        try:
            from docx import Document  # type: ignore[import-untyped]
        except ImportError as exc:
            raise DocumentParsingError(
                str(path), "python-docx is not installed"
            ) from exc

        if not path.exists():
            raise DocumentParsingError(str(path), "File does not exist")

        try:
            doc = Document(str(path))
            paragraphs: list[str] = []
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    paragraphs.append(text)

            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text = cell.text.strip()
                        if text:
                            paragraphs.append(text)

            full_text = "\n".join(paragraphs)
            logger.info(
                "Extracted %d characters from %s (%d paragraphs)",
                len(full_text), path.name, len(paragraphs),
            )
            return full_text
        except Exception as exc:
            raise DocumentParsingError(str(path), str(exc)) from exc

    def supported_extensions(self) -> tuple[str, ...]:
        return (".docx",)


class DocumentProcessorFactory:
    """Factory that returns the appropriate :class:`DocumentProcessor` for a file.

    Extensible: register new processors via :meth:`register`.
    """

    _processors: dict[str, DocumentProcessor] = {}

    @classmethod
    def register(cls, processor: DocumentProcessor) -> None:
        """Register a processor for its supported extensions."""
        for ext in processor.supported_extensions():
            cls._processors[ext.lower()] = processor
            logger.debug("Registered processor for '%s'", ext)

    @classmethod
    def create(cls, path: Path) -> DocumentProcessor:
        """Get a processor for the given file's extension.

        Args:
            path: Path to the document file.

        Returns:
            A suitable :class:`DocumentProcessor`.

        Raises:
            UnsupportedFormatError: If no processor is registered.
        """
        ext = path.suffix.lower()
        processor = cls._processors.get(ext)
        if processor is None:
            raise UnsupportedFormatError(str(path), ext)
        return processor

    @classmethod
    def register_defaults(cls) -> None:
        """Register built-in processors."""
        cls.register(DocxProcessor())
