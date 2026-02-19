"""Document text extraction from .docx, .txt, and .pdf files."""

from __future__ import annotations

from pathlib import Path

from utils.exceptions import DocumentParsingError, UnsupportedFormatError
from utils.logging_config import get_logger

logger = get_logger("core.document_processor")


class DocxProcessor:
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


class TxtProcessor:
    """Extract text from plain ``.txt`` files."""

    def extract_text(self, path: Path) -> str:
        if not path.exists():
            raise DocumentParsingError(str(path), "File does not exist")

        for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
            try:
                text = path.read_text(encoding=encoding)
                logger.info(
                    "Extracted %d characters from %s (encoding=%s)",
                    len(text), path.name, encoding,
                )
                return text
            except UnicodeDecodeError:
                continue
            except OSError as exc:
                raise DocumentParsingError(str(path), str(exc)) from exc

        raise DocumentParsingError(str(path), "Could not decode file with any supported encoding")


class PdfProcessor:
    """Extract text from ``.pdf`` files using *pypdf*."""

    def extract_text(self, path: Path) -> str:
        try:
            from pypdf import PdfReader  # type: ignore[import-untyped]
        except ImportError as exc:
            raise DocumentParsingError(
                str(path), "pypdf is not installed"
            ) from exc

        if not path.exists():
            raise DocumentParsingError(str(path), "File does not exist")

        try:
            reader = PdfReader(str(path))
            pages: list[str] = []
            for page in reader.pages:
                page_text = page.extract_text() or ""
                page_text = page_text.strip()
                if page_text:
                    pages.append(page_text)

            full_text = "\n".join(pages)
            logger.info(
                "Extracted %d characters from %s (%d pages)",
                len(full_text), path.name, len(reader.pages),
            )
            return full_text
        except Exception as exc:
            raise DocumentParsingError(str(path), str(exc)) from exc


_PROCESSORS: dict[str, type[DocxProcessor] | type[TxtProcessor] | type[PdfProcessor]] = {
    ".docx": DocxProcessor,
    ".txt": TxtProcessor,
    ".pdf": PdfProcessor,
}


def get_processor(path: Path) -> DocxProcessor | TxtProcessor | PdfProcessor:
    """Return a processor for the given file, or raise if unsupported.

    Args:
        path: Path to the document file.

    Returns:
        A processor instance for the detected file format.

    Raises:
        UnsupportedFormatError: If the file extension is not supported.
    """
    suffix = path.suffix.lower()
    processor_cls = _PROCESSORS.get(suffix)
    if processor_cls is None:
        raise UnsupportedFormatError(str(path), suffix)
    return processor_cls()
