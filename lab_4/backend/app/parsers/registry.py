from collections.abc import Callable
from pathlib import Path


def parse_pdf(path: Path) -> str:
    import pdfplumber

    text_parts: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text_parts.append(extracted)
    return "\n".join(text_parts)


def parse_docx(path: Path) -> str:
    from docx import Document

    doc = Document(str(path))
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())


def parse_rtf(path: Path) -> str:
    from striprtf.striprtf import rtf_to_text

    raw = path.read_text(encoding="utf-8", errors="replace")
    return rtf_to_text(raw)


def parse_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


PARSERS: dict[str, Callable[[Path], str]] = {
    ".pdf": parse_pdf,
    ".docx": parse_docx,
    ".rtf": parse_rtf,
    ".txt": parse_txt,
}


def parse(path: Path, ext: str) -> str:
    """Unified entry point. ext should be lowercase with leading dot, e.g. '.pdf'."""
    parser = PARSERS.get(ext)
    if parser is None:
        raise ValueError(f"Unsupported file extension: {ext!r}. Supported: {list(PARSERS)}")
    return parser(path)
