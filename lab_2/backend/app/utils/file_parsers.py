"""Extract plain text from uploaded files (TXT, PDF, DOCX, RTF)."""
from __future__ import annotations

import io
from fastapi import UploadFile, HTTPException


async def extract_text(file: UploadFile) -> str:
    content = await file.read()
    filename = (file.filename or "").lower()
    content_type = (file.content_type or "").lower()

    if filename.endswith(".txt") or "text/plain" in content_type:
        return _parse_txt(content)
    if filename.endswith(".pdf") or "pdf" in content_type:
        return _parse_pdf(content)
    if filename.endswith(".docx") or "wordprocessingml" in content_type or "docx" in content_type:
        return _parse_docx(content)
    if filename.endswith(".rtf") or "rtf" in content_type:
        return _parse_rtf(content)

    # Fallback: try UTF-8 decode
    try:
        return content.decode("utf-8", errors="replace")
    except Exception:
        raise HTTPException(status_code=415, detail=f"Unsupported file format: {filename}")


def _parse_txt(content: bytes) -> str:
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="replace")


def _parse_pdf(content: bytes) -> str:
    try:
        import PyPDF2

        reader = PyPDF2.PdfReader(io.BytesIO(content))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n".join(pages)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse PDF: {exc}")


def _parse_docx(content: bytes) -> str:
    try:
        from docx import Document

        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse DOCX: {exc}")


def _parse_rtf(content: bytes) -> str:
    try:
        from striprtf.striprtf import rtf_to_text

        raw = content.decode("utf-8", errors="replace")
        return rtf_to_text(raw)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse RTF: {exc}")
