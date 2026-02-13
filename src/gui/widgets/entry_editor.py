"""Entry editor panel for viewing and editing a single dictionary entry."""

from __future__ import annotations

from copy import deepcopy

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from models.enums import PartOfSpeech
from models.lexeme import DictionaryEntry, MorphologicalFeature, WordForm


class EntryEditor(QWidget):
    """Right-side panel for editing a selected dictionary entry.

    Signals:
        entry_saved: Emitted with the modified :class:`DictionaryEntry`.
        entry_cancelled: Emitted when the user cancels editing.
    """

    entry_saved = pyqtSignal(object)    # DictionaryEntry
    entry_cancelled = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_entry: DictionaryEntry | None = None

        self._setup_ui()
        self.clear()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # --- Basic fields ---
        form_group = QGroupBox("Entry Details")
        form_layout = QFormLayout(form_group)

        self._lexeme_edit = QLineEdit()
        self._lexeme_edit.setReadOnly(True)
        self._lexeme_edit.setPlaceholderText("Select an entry...")
        form_layout.addRow("Lexeme:", self._lexeme_edit)

        self._stem_edit = QLineEdit()
        form_layout.addRow("Stem:", self._stem_edit)

        self._pos_combo = QComboBox()
        for pos in PartOfSpeech:
            self._pos_combo.addItem(pos.value, pos)
        form_layout.addRow("POS:", self._pos_combo)

        self._freq_spin = QSpinBox()
        self._freq_spin.setRange(0, 999_999)
        form_layout.addRow("Frequency:", self._freq_spin)

        self._irregular_combo = QComboBox()
        self._irregular_combo.addItem("No", False)
        self._irregular_combo.addItem("Yes", True)
        form_layout.addRow("Irregular:", self._irregular_combo)

        self._definition_edit = QTextEdit()
        self._definition_edit.setPlaceholderText("No definition — right-click word to generate")
        self._definition_edit.setMinimumHeight(54)
        self._definition_edit.setMaximumHeight(80)
        form_layout.addRow("Definition:", self._definition_edit)

        layout.addWidget(form_group)

        # --- Word forms table ---
        forms_group = QGroupBox("Word Forms")
        forms_layout = QVBoxLayout(forms_group)

        self._forms_table = QTableWidget()
        self._forms_table.setColumnCount(3)
        self._forms_table.setHorizontalHeaderLabels(["Form", "Ending", "Features"])
        self._forms_table.horizontalHeader().setStretchLastSection(True)
        self._forms_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self._forms_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        forms_layout.addWidget(self._forms_table)

        forms_buttons = QHBoxLayout()
        self._btn_add_form = QPushButton("Add Form")
        self._btn_add_form.clicked.connect(self._add_form_row)
        self._btn_remove_form = QPushButton("Remove Form")
        self._btn_remove_form.clicked.connect(self._remove_form_row)
        forms_buttons.addWidget(self._btn_add_form)
        forms_buttons.addWidget(self._btn_remove_form)
        forms_buttons.addStretch()
        forms_layout.addLayout(forms_buttons)

        layout.addWidget(forms_group, stretch=1)

        # --- Notes ---
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_group)
        self._notes_edit = QTextEdit()
        self._notes_edit.setMaximumHeight(80)
        notes_layout.addWidget(self._notes_edit)
        layout.addWidget(notes_group)

        # --- Buttons ---
        buttons = QHBoxLayout()
        self._btn_save = QPushButton("Save")
        self._btn_save.clicked.connect(self._on_save)
        self._btn_cancel = QPushButton("Cancel")
        self._btn_cancel.clicked.connect(self._on_cancel)
        buttons.addStretch()
        buttons.addWidget(self._btn_save)
        buttons.addWidget(self._btn_cancel)
        layout.addLayout(buttons)

    # --- Public API ---

    def load_entry(self, entry: DictionaryEntry | None) -> None:
        """Populate the editor with an entry."""
        self._current_entry = deepcopy(entry) if entry else None
        if entry is None:
            self.clear()
            return

        self._lexeme_edit.setText(entry.lexeme)
        self._stem_edit.setText(entry.stem)

        idx = self._pos_combo.findData(entry.pos)
        if idx >= 0:
            self._pos_combo.setCurrentIndex(idx)

        self._freq_spin.setValue(entry.frequency)
        self._irregular_combo.setCurrentIndex(1 if entry.irregular else 0)
        self._definition_edit.setPlainText(entry.definition)
        self._notes_edit.setPlainText(entry.notes)

        # Populate word forms table
        self._forms_table.setRowCount(0)
        for wf in entry.word_forms:
            self._append_form_row(wf.form, wf.ending, wf.features.summary())

        self._set_enabled(True)

    def clear(self) -> None:
        """Clear all fields."""
        self._current_entry = None
        self._lexeme_edit.clear()
        self._stem_edit.clear()
        self._pos_combo.setCurrentIndex(0)
        self._freq_spin.setValue(0)
        self._irregular_combo.setCurrentIndex(0)
        self._definition_edit.clear()
        self._notes_edit.clear()
        self._forms_table.setRowCount(0)
        self._set_enabled(False)

    def set_new_entry_mode(self, lexeme: str = "") -> None:
        """Switch to 'create new entry' mode."""
        self.clear()
        self._lexeme_edit.setReadOnly(False)
        self._lexeme_edit.setText(lexeme)
        self._set_enabled(True)

    # --- Internal ---

    def _set_enabled(self, enabled: bool) -> None:
        self._stem_edit.setEnabled(enabled)
        self._pos_combo.setEnabled(enabled)
        self._freq_spin.setEnabled(enabled)
        self._irregular_combo.setEnabled(enabled)
        self._definition_edit.setEnabled(enabled)
        self._notes_edit.setEnabled(enabled)
        self._forms_table.setEnabled(enabled)
        self._btn_add_form.setEnabled(enabled)
        self._btn_remove_form.setEnabled(enabled)
        self._btn_save.setEnabled(enabled)
        self._btn_cancel.setEnabled(enabled)

    def _append_form_row(self, form: str, ending: str, features: str) -> None:
        row = self._forms_table.rowCount()
        self._forms_table.insertRow(row)
        self._forms_table.setItem(row, 0, QTableWidgetItem(form))
        self._forms_table.setItem(row, 1, QTableWidgetItem(ending))
        self._forms_table.setItem(row, 2, QTableWidgetItem(features))

    def _add_form_row(self) -> None:
        self._append_form_row("", "", "")

    def _remove_form_row(self) -> None:
        row = self._forms_table.currentRow()
        if row >= 0:
            self._forms_table.removeRow(row)

    def _collect_entry(self) -> DictionaryEntry | None:
        """Build a DictionaryEntry from current editor state."""
        lexeme = self._lexeme_edit.text().strip()
        if not lexeme:
            QMessageBox.warning(self, "Validation", "Lexeme cannot be empty.")
            return None

        stem = self._stem_edit.text().strip() or lexeme
        pos = self._pos_combo.currentData()
        freq = self._freq_spin.value()
        irregular = self._irregular_combo.currentData()
        definition = self._definition_edit.toPlainText().strip()
        notes = self._notes_edit.toPlainText().strip()

        word_forms: list[WordForm] = []
        for row in range(self._forms_table.rowCount()):
            form_item = self._forms_table.item(row, 0)
            ending_item = self._forms_table.item(row, 1)
            feat_item = self._forms_table.item(row, 2)

            form_text = form_item.text().strip() if form_item else ""
            ending_text = ending_item.text().strip() if ending_item else ""
            feat_text = feat_item.text().strip() if feat_item else ""

            if form_text:
                features = self._parse_features(feat_text)
                word_forms.append(WordForm(form=form_text, ending=ending_text, features=features))

        return DictionaryEntry(
            lexeme=lexeme,
            stem=stem,
            pos=pos,
            frequency=freq,
            word_forms=word_forms,
            irregular=irregular,
            notes=notes,
            definition=definition,
        )

    @staticmethod
    def _parse_features(text: str) -> MorphologicalFeature:
        """Parse a 'key=value, key=value' string into MorphologicalFeature."""
        feat = MorphologicalFeature()
        if not text:
            return feat
        for part in text.split(","):
            part = part.strip()
            if "=" in part:
                key, val = part.split("=", 1)
                key, val = key.strip(), val.strip()
                if hasattr(feat, key):
                    setattr(feat, key, val)
        return feat

    def _on_save(self) -> None:
        entry = self._collect_entry()
        if entry:
            self._lexeme_edit.setReadOnly(True)
            self.entry_saved.emit(entry)

    def _on_cancel(self) -> None:
        if self._current_entry:
            self.load_entry(self._current_entry)
        else:
            self.clear()
        self._lexeme_edit.setReadOnly(True)
        self.entry_cancelled.emit()
