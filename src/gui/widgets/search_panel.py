"""Search and filter panel widget."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QWidget,
)

from models.enums import PartOfSpeech


class SearchPanel(QWidget):
    """Combined search bar and filter controls.

    Signals:
        search_requested: Emitted when the user triggers a search.
            Carries ``(query, pos_filter, min_freq, max_freq, use_regex)``.
    """

    search_requested = pyqtSignal(str, object, int, int, bool)
    # (query, PartOfSpeech | None, min_freq, max_freq, use_regex)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        # Search field
        layout.addWidget(QLabel("Search:"))
        self._query_edit = QLineEdit()
        self._query_edit.setPlaceholderText("Enter search query (wildcards: * ?)")
        self._query_edit.returnPressed.connect(self._emit_search)
        layout.addWidget(self._query_edit, stretch=2)

        # Regex toggle
        self._regex_check = QCheckBox("Regex")
        layout.addWidget(self._regex_check)

        # POS filter
        layout.addWidget(QLabel("POS:"))
        self._pos_combo = QComboBox()
        self._pos_combo.addItem("All", None)
        for pos in PartOfSpeech:
            self._pos_combo.addItem(pos.value, pos)
        self._pos_combo.currentIndexChanged.connect(self._emit_search)
        layout.addWidget(self._pos_combo)

        # Frequency range
        layout.addWidget(QLabel("Freq:"))
        self._min_freq = QSpinBox()
        self._min_freq.setRange(0, 999_999)
        self._min_freq.setSpecialValueText("Min")
        layout.addWidget(self._min_freq)

        layout.addWidget(QLabel("-"))
        self._max_freq = QSpinBox()
        self._max_freq.setRange(0, 999_999)
        self._max_freq.setSpecialValueText("Max")
        layout.addWidget(self._max_freq)

        # Search button
        self._btn_search = QPushButton("Search")
        self._btn_search.clicked.connect(self._emit_search)
        layout.addWidget(self._btn_search)

        # Clear button
        self._btn_clear = QPushButton("Clear")
        self._btn_clear.clicked.connect(self._clear_and_search)
        layout.addWidget(self._btn_clear)

    def _emit_search(self) -> None:
        query = self._query_edit.text().strip()
        pos_filter = self._pos_combo.currentData()
        min_freq = self._min_freq.value()
        max_freq = self._max_freq.value()
        use_regex = self._regex_check.isChecked()
        self.search_requested.emit(query, pos_filter, min_freq, max_freq, use_regex)

    def _clear_and_search(self) -> None:
        self._query_edit.clear()
        self._pos_combo.setCurrentIndex(0)
        self._min_freq.setValue(0)
        self._max_freq.setValue(0)
        self._regex_check.setChecked(False)
        self._emit_search()
