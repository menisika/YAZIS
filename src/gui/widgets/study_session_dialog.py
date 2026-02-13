"""Full study session dialog with flashcard display and controls."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from PyQt6.QtCore import QObject, QThread, Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.sound_manager import SoundManager
from core.study_manager import StudyManager
from gui.widgets.flashcard_widget import FlashcardWidget
from models.lexeme import DictionaryEntry

if TYPE_CHECKING:
    from core.definition_service import DefinitionService
    from core.rule_engine import RuleEngine


class _DefinitionFetchWorker(QObject):
    """Background worker to batch-fetch definitions."""

    progress = pyqtSignal(int, int)  # (completed, total)
    finished = pyqtSignal(dict)       # {lexeme: definition}
    error = pyqtSignal(str)

    def __init__(self, service: DefinitionService, entries: list[DictionaryEntry]) -> None:
        super().__init__()
        self._service = service
        self._entries = entries

    def run(self) -> None:
        try:
            results = self._service.fetch_definitions_batch(
                self._entries,
                progress_callback=lambda c, t: self.progress.emit(c, t),
            )
            self.finished.emit(results)
        except Exception as exc:
            self.error.emit(str(exc))


class StudySessionDialog(QDialog):
    """Main study session dialog.

    Displays flashcards one by one with flip animation, and records
    user responses.

    Args:
        entries: The entries to study.
        mode: One of ``word_to_def``, ``def_to_word``, ``word_form_practice``.
        study_manager: For recording results.
        definition_service: For pre-fetching definitions.
        sound_manager: For audio feedback.
        rule_engine: For word form practice mode.
        flip_speed: Animation speed key.
        auto_advance: Auto-advance after response.
        parent: Parent widget.
    """

    def __init__(
        self,
        entries: list[DictionaryEntry],
        mode: str,
        study_manager: StudyManager,
        definition_service: DefinitionService | None,
        sound_manager: SoundManager,
        rule_engine: RuleEngine | None = None,
        flip_speed: str = "normal",
        auto_advance: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._entries = entries
        self._mode = mode
        self._study = study_manager
        self._def_service = definition_service
        self._sound = sound_manager
        self._rule_engine = rule_engine
        self._auto_advance = auto_advance
        self._index = 0
        self._known_count = 0
        self._answered = False

        # For word_form_practice: store the target form for current card
        self._current_target_form = ""

        self.setWindowTitle("Study Session")
        self.setMinimumSize(550, 420)
        self.resize(600, 480)

        self._setup_ui(flip_speed)
        self._setup_shortcuts()

        if entries:
            self._load_card(0)

    def _setup_ui(self, flip_speed: str) -> None:
        layout = QVBoxLayout(self)

        # Header
        header = QHBoxLayout()
        mode_labels = {
            "word_to_def": "Word -> Definition",
            "def_to_word": "Definition -> Word",
            "word_form_practice": "Word Form Practice",
        }
        self._mode_label = QLabel(f"<b>{mode_labels.get(self._mode, self._mode)}</b>")
        header.addWidget(self._mode_label)
        header.addStretch()
        self._progress_label = QLabel()
        header.addWidget(self._progress_label)
        layout.addLayout(header)

        # Flashcard
        self._card = FlashcardWidget()
        self._card.set_speed(flip_speed)
        self._card.flipped.connect(self._on_flipped)
        layout.addWidget(self._card, stretch=1)

        # Flip button
        self._btn_flip = QPushButton("Flip Card  (Space)")
        self._btn_flip.setFixedHeight(36)
        self._btn_flip.clicked.connect(self._on_flip)
        layout.addWidget(self._btn_flip)

        # Response buttons (hidden until flipped)
        resp_layout = QHBoxLayout()
        self._btn_know = QPushButton("I Know This  (K)")
        self._btn_know.setFixedHeight(36)
        self._btn_know.clicked.connect(self._on_know)
        resp_layout.addWidget(self._btn_know)

        self._btn_practice = QPushButton("Need Practice  (N)")
        self._btn_practice.setFixedHeight(36)
        self._btn_practice.clicked.connect(self._on_practice)
        resp_layout.addWidget(self._btn_practice)
        layout.addLayout(resp_layout)

        # Skip / Exit
        bottom = QHBoxLayout()
        self._btn_skip = QPushButton("Skip  (S)")
        self._btn_skip.clicked.connect(self._on_skip)
        bottom.addWidget(self._btn_skip)
        bottom.addStretch()
        self._btn_exit = QPushButton("Exit")
        self._btn_exit.clicked.connect(self._on_exit)
        bottom.addWidget(self._btn_exit)
        layout.addLayout(bottom)

        self._set_response_visible(False)

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence(Qt.Key.Key_Space), self).activated.connect(self._on_flip)
        QShortcut(QKeySequence(Qt.Key.Key_K), self).activated.connect(self._on_know)
        QShortcut(QKeySequence(Qt.Key.Key_N), self).activated.connect(self._on_practice)
        QShortcut(QKeySequence(Qt.Key.Key_S), self).activated.connect(self._on_skip)

    # --- Pre-fetch definitions ---

    def prefetch_definitions(self) -> None:
        """Check for missing definitions and fetch them before starting."""
        if self._def_service is None or not self._def_service.api_key:
            return
        if self._mode == "word_form_practice":
            return

        need_defs = [e for e in self._entries if not e.definition]
        if not need_defs:
            return

        progress = QProgressDialog(
            "Fetching definitions...", "Skip", 0, len(need_defs), self
        )
        progress.setWindowTitle("Preparing Session")
        progress.setMinimumDuration(0)
        progress.setValue(0)

        self._fetch_thread = QThread()
        self._fetch_worker = _DefinitionFetchWorker(self._def_service, need_defs)
        self._fetch_worker.moveToThread(self._fetch_thread)

        self._fetch_thread.started.connect(self._fetch_worker.run)
        self._fetch_worker.progress.connect(
            lambda c, t: progress.setValue(c)
        )

        def on_finished(results: dict[str, str]) -> None:
            for entry in self._entries:
                if entry.lexeme in results:
                    entry.definition = results[entry.lexeme]
            progress.close()
            self._fetch_thread.quit()
            # Reload current card in case definition was just fetched
            if self._entries:
                self._load_card(self._index)

        def on_error(msg: str) -> None:
            progress.close()
            self._fetch_thread.quit()

        self._fetch_worker.finished.connect(on_finished)
        self._fetch_worker.error.connect(on_error)
        self._fetch_thread.finished.connect(lambda: None)

        progress.canceled.connect(lambda: self._fetch_thread.quit())

        self._fetch_thread.start()

    # --- Card loading ---

    def _load_card(self, index: int) -> None:
        """Load a card by index."""
        self._index = index
        self._answered = False
        total = len(self._entries)
        self._progress_label.setText(f"Card {index + 1} of {total}")

        if index >= total:
            self._on_session_complete()
            return

        entry = self._entries[index]

        if self._mode == "word_to_def":
            front = entry.lexeme
            back = entry.definition or f"({entry.pos.value}) — no definition available"
        elif self._mode == "def_to_word":
            front = entry.definition or f"(No definition for this {entry.pos.value})"
            back = entry.lexeme
        elif self._mode == "word_form_practice":
            front, back = self._prepare_word_form_card(entry)
        else:
            front = entry.lexeme
            back = entry.definition or entry.notes or str(entry.pos)

        self._card.set_front(front)
        self._card.set_back(back)
        self._card.reset()
        self._set_response_visible(False)
        self._btn_flip.setEnabled(True)

    def _prepare_word_form_card(self, entry: DictionaryEntry) -> tuple[str, str]:
        """Prepare front/back text for word form practice mode."""
        if not entry.word_forms:
            return entry.lexeme, entry.lexeme

        # Pick a random word form that differs from the base
        candidates = [wf for wf in entry.word_forms if wf.form != entry.lexeme]
        if not candidates:
            candidates = entry.word_forms

        target = random.choice(candidates)
        self._current_target_form = target.form
        feature_desc = target.features.summary()
        front = f"{entry.lexeme}\n\nWhat is the {feature_desc} form?"
        back = target.form
        return front, back

    # --- User actions ---

    def _on_flip(self) -> None:
        if not self._card.is_animating and not self._card.is_flipped:
            self._sound.play("whoosh")
            self._card.flip()

    def _on_flipped(self) -> None:
        if self._card.is_flipped:
            self._set_response_visible(True)
            self._btn_flip.setEnabled(False)

    def _on_know(self) -> None:
        if not self._card.is_flipped or self._answered:
            return
        self._answered = True
        entry = self._entries[self._index]
        self._study.record_result(entry.lexeme, known=True)
        self._known_count += 1
        self._sound.play("ding")
        if self._auto_advance:
            self._advance()

    def _on_practice(self) -> None:
        if not self._card.is_flipped or self._answered:
            return
        self._answered = True
        entry = self._entries[self._index]
        self._study.record_result(entry.lexeme, known=False)
        if self._auto_advance:
            self._advance()

    def _on_skip(self) -> None:
        self._advance()

    def _advance(self) -> None:
        """Move to the next card."""
        next_idx = self._index + 1
        if next_idx >= len(self._entries):
            self._on_session_complete()
        else:
            self._load_card(next_idx)

    def _on_exit(self) -> None:
        self._study.save()
        self.reject()

    def _on_session_complete(self) -> None:
        self._study.save()
        self._sound.play("tada")
        total = len(self._entries)
        QMessageBox.information(
            self,
            "Session Complete",
            f"You completed all {total} cards!\n\n"
            f"Known: {self._known_count}\n"
            f"Need practice: {total - self._known_count}",
        )
        self.accept()

    # --- Helpers ---

    def _set_response_visible(self, visible: bool) -> None:
        self._btn_know.setVisible(visible)
        self._btn_practice.setVisible(visible)
