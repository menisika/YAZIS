"""Dialog for generating and exporting ESL practice tasks via the LLM service."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.llm_service import LLMService
from core.task_pdf_exporter import TaskPDFExporter


class _TaskWorker(QThread):
    """Background worker that calls LLMService.generate_task()."""

    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, llm_service: LLMService, words: list[tuple[str, str]]) -> None:
        super().__init__()
        self._llm_service = llm_service
        self._words = words

    def run(self) -> None:
        try:
            result = self._llm_service.generate_task(self._words)
            self.result_ready.emit(result)
        except Exception as exc:
            self.error_occurred.emit(str(exc))


class TaskGeneratorDialog(QDialog):
    """
    Display generated ESL exercises for a set of selected lemmas.

    Generation starts automatically when the dialog is shown.
    The user can export the result to PDF once generation completes.

    Args:
        word_pos_pairs: List of ``(lexeme, pos)`` tuples.
        llm_service: Configured :class:`LLMService` instance.
        parent: Optional parent widget.

    """

    def __init__(
        self,
        word_pos_pairs: list[tuple[str, str]],
        llm_service: LLMService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._word_pos_pairs = word_pos_pairs
        self._llm_service = llm_service
        self._worker: _TaskWorker | None = None
        self._result: str = ""

        self.setWindowTitle("Generate Task")
        self.setMinimumSize(700, 500)
        self._build_ui()
        self._start_generation()

    # --- UI construction ---

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        summary = ", ".join(
            f"{lex} ({pos.lower()})" for lex, pos in self._word_pos_pairs
        )
        words_label = QLabel(f"Lexemes: {summary}")
        words_label.setWordWrap(True)
        layout.addWidget(words_label)

        self._status_label = QLabel("Generating exercises…")
        layout.addWidget(self._status_label)

        self._text_area = QTextEdit()
        self._text_area.setReadOnly(True)
        self._text_area.setPlaceholderText("Response will appear here…")
        layout.addWidget(self._text_area, stretch=1)

        # Buttons
        self._btn_export = QPushButton("Export PDF…")
        self._btn_export.setEnabled(False)
        self._btn_export.clicked.connect(self._on_export_pdf)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        button_box.addButton(self._btn_export, QDialogButtonBox.ButtonRole.ActionRole)

        layout.addWidget(button_box)

    # --- Generation ---

    def _start_generation(self) -> None:
        self._worker = _TaskWorker(self._llm_service, self._word_pos_pairs)
        self._worker.result_ready.connect(self._on_result)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.start()

    def _on_result(self, text: str) -> None:
        self._result = text
        self._text_area.setMarkdown(text)
        self._status_label.setText("Done.")
        self._btn_export.setEnabled(True)

    def _on_error(self, message: str) -> None:
        self._status_label.setText("Error.")
        QMessageBox.critical(self, "Generation Failed", message)

    # --- PDF export ---

    def _on_export_pdf(self) -> None:
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Export Task as PDF",
            "esl_exercises.pdf",
            "PDF Files (*.pdf)",
        )
        if not path_str:
            return
        try:
            lexemes = ", ".join(lex for lex, _ in self._word_pos_pairs)
            exporter = TaskPDFExporter(title=f"ESL Exercises: {lexemes}")
            exporter.export(self._result, Path(path_str))
            QMessageBox.information(
                self,
                "Export Complete",
                f"PDF saved to:\n{path_str}",
            )
        except Exception as exc:
            QMessageBox.critical(self, "Export Failed", str(exc))

    # --- Cleanup ---

    def closeEvent(self, event):  # type: ignore[override]
        if self._worker and self._worker.isRunning():
            self._worker.quit()
            self._worker.wait(2000)
        super().closeEvent(event)
