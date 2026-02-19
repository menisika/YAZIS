"""PDF export for generated ESL task content."""

from __future__ import annotations

from pathlib import Path

from utils.logging_config import get_logger

logger = get_logger("core.task_pdf_exporter")

# Replace common Unicode typographic characters before Markdown→HTML conversion
# to avoid encoding issues with fpdf2's core Latin-1 fonts.
_ASCII_MAP = str.maketrans({
    "\u2018": "'",    # left single quotation mark
    "\u2019": "'",    # right single quotation mark
    "\u201c": '"',    # left double quotation mark
    "\u201d": '"',    # right double quotation mark
    "\u2013": "-",    # en dash
    "\u2014": "--",   # em dash
    "\u2026": "...",  # ellipsis
    "\u2022": "-",    # bullet (keep as list marker)
    "\u2192": "->",   # right arrow
    "\u00a0": " ",    # non-breaking space
    "\u2212": "-",    # minus sign
})


def _sanitize(text: str) -> str:
    return text.translate(_ASCII_MAP)


class TaskPDFExporter:
    """Export Markdown task content to a PDF file.

    Markdown is converted to HTML via the ``markdown`` library and then
    rendered by fpdf2's built-in HTML engine.

    Args:
        title: Document title shown as an H1 at the top of the first page.
    """

    def __init__(self, title: str = "ESL Practice Exercises") -> None:
        self._title = title

    def export(self, markdown_text: str, path: Path) -> None:
        """Convert *markdown_text* to a styled PDF at *path*.

        Args:
            markdown_text: Markdown-formatted response from the LLM.
            path: Destination file path (parent dirs are created as needed).

        Raises:
            OSError: If the file cannot be written.
        """
        import markdown as md  # type: ignore[import-untyped]
        from fpdf import FPDF  # type: ignore[import-untyped]

        safe_md = _sanitize(markdown_text)
        body_html = md.markdown(safe_md, extensions=["extra"])
        title_html = f"<h2>{_sanitize(self._title)}</h2>"
        full_html = title_html + body_html

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", size=11)
        pdf.write_html(full_html)

        path.parent.mkdir(parents=True, exist_ok=True)
        pdf.output(str(path))
        logger.info("Task PDF exported to %s", path)
