"""Controller for document loading and analysis (runs in QThread)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QProgressDialog

from core.document_processor import DocumentProcessorFactory
from core.lexical_analyzer import LexicalAnalyzer
from core.morphological_analyzer import MorphologicalAnalyzer
from core.rule_engine import RuleEngine
from core.stem_extractor import StemExtractor
from core.dictionary_manager import DictionaryManager
from models.enums import PartOfSpeech
from models.lexeme import DictionaryEntry
from utils.exceptions import DocumentError, AnalysisError
from utils.logging_config import get_logger

if TYPE_CHECKING:
    from gui.main_window import MainWindow

logger = get_logger("gui.document_controller")


class AnalysisWorker(QObject):
    """Background worker that runs the full NLP pipeline on a document.

    Signals:
        progress: ``(step_name, percentage)``
        finished: ``(list[DictionaryEntry], source_filename)``
        error: ``(error_message,)``
    """

    progress = pyqtSignal(str, int)
    finished = pyqtSignal(list, str)
    error = pyqtSignal(str)

    def __init__(
        self,
        path: Path,
        lexical_analyzer: LexicalAnalyzer,
        morphological_analyzer: MorphologicalAnalyzer,
        stem_extractor: StemExtractor,
        rule_engine: RuleEngine,
    ) -> None:
        super().__init__()
        self._path = path
        self._lexical = lexical_analyzer
        self._morph = morphological_analyzer
        self._stem = stem_extractor
        self._rule = rule_engine

    def run(self) -> None:
        try:
            # Step 1: Extract text
            self.progress.emit("Extracting text...", 10)
            processor = DocumentProcessorFactory.create(self._path)
            text = processor.extract_text(self._path)

            # Step 2: Lexical analysis
            self.progress.emit("Tokenizing and extracting lexemes...", 30)
            freq_map, pos_map, forms_map = self._lexical.extract_lexemes(text)

            # Step 3: Stem extraction
            self.progress.emit("Extracting stems...", 50)
            stem_map = self._stem.extract_batch(list(freq_map.keys()))

            # Step 4: Morphological analysis
            self.progress.emit("Analyzing morphology...", 70)
            lemmas = list(freq_map.keys())
            word_forms_map = self._morph.analyze(lemmas, pos_map, forms_map)

            # Step 5: Build entries
            self.progress.emit("Building dictionary entries...", 90)
            entries: list[DictionaryEntry] = []
            for lemma in lemmas:
                pos = pos_map.get(lemma, PartOfSpeech.OTHER)
                stem = stem_map.get(lemma, lemma)
                freq = freq_map.get(lemma, 0)
                wf_list = word_forms_map.get(lemma, [])
                irregular = self._rule.is_irregular(lemma, pos)

                # Supplement with rule-generated forms
                try:
                    generated = self._rule.generate_all_forms(lemma, pos)
                    seen = {wf.form for wf in wf_list}
                    for gf in generated:
                        if gf.form not in seen:
                            wf_list.append(gf)
                            seen.add(gf.form)
                except Exception:
                    pass  # Non-critical; keep observed forms

                entry = DictionaryEntry(
                    lexeme=lemma,
                    stem=stem,
                    pos=pos,
                    frequency=freq,
                    word_forms=wf_list,
                    irregular=irregular,
                )
                entries.append(entry)

            self.progress.emit("Done", 100)
            self.finished.emit(entries, self._path.name)

        except (DocumentError, AnalysisError) as exc:
            self.error.emit(str(exc))
        except Exception as exc:
            logger.exception("Unexpected error during analysis")
            self.error.emit(f"Unexpected error: {exc}")


class DocumentController:
    """Orchestrates document loading and analysis in a background thread.

    Args:
        manager: The dictionary manager to populate.
        lexical_analyzer: Lexical analysis component.
        morphological_analyzer: Morphological analysis component.
        stem_extractor: Stem extraction component.
        rule_engine: Rule engine for form generation.
        main_window: The main application window.
    """

    def __init__(
        self,
        manager: DictionaryManager,
        lexical_analyzer: LexicalAnalyzer,
        morphological_analyzer: MorphologicalAnalyzer,
        stem_extractor: StemExtractor,
        rule_engine: RuleEngine,
        main_window: MainWindow,
    ) -> None:
        self._manager = manager
        self._lexical = lexical_analyzer
        self._morph = morphological_analyzer
        self._stem = stem_extractor
        self._rule = rule_engine
        self._window = main_window
        self._thread: QThread | None = None
        self._worker: AnalysisWorker | None = None

    def load_document(self, path: Path) -> None:
        """Start document loading and analysis in a background thread.

        Args:
            path: Path to the ``.docx`` file.
        """
        if self._thread is not None and self._thread.isRunning():
            QMessageBox.warning(
                self._window,
                "Busy",
                "An analysis is already in progress. Please wait.",
            )
            return

        self._window.update_status(f"Loading {path.name}...")

        # Progress dialog
        self._progress = QProgressDialog(
            "Analyzing document...", "Cancel", 0, 100, self._window
        )
        self._progress.setWindowTitle("Document Analysis")
        self._progress.setMinimumDuration(0)
        self._progress.setValue(0)

        # Worker + thread
        self._thread = QThread()
        self._worker = AnalysisWorker(
            path, self._lexical, self._morph, self._stem, self._rule
        )
        self._worker.moveToThread(self._thread)

        # Connect signals
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup)

        self._progress.canceled.connect(self._on_cancel)

        self._thread.start()

    def _on_progress(self, step: str, pct: int) -> None:
        self._progress.setLabelText(step)
        self._progress.setValue(pct)
        self._window.update_status(step)

    def _on_finished(self, entries: list[DictionaryEntry], filename: str) -> None:
        self._progress.close()
        self._manager.bulk_add(entries)
        # Record source document
        if filename not in self._manager.dictionary.metadata.source_documents:
            self._manager.dictionary.metadata.source_documents.append(filename)
        self._window.update_status(
            f"Loaded {len(entries)} lexemes from {filename}"
        )
        logger.info("Document analysis complete: %d entries from %s", len(entries), filename)

    def _on_error(self, message: str) -> None:
        self._progress.close()
        QMessageBox.critical(
            self._window, "Analysis Error", message
        )
        self._window.update_status("Analysis failed")
        logger.error("Document analysis error: %s", message)

    def _on_cancel(self) -> None:
        if self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(3000)
        self._window.update_status("Analysis cancelled")

    def _cleanup(self) -> None:
        self._worker = None
        self._thread = None
