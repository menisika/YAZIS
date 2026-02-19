"""Dictionary table view widget with sorting and pagination."""

from __future__ import annotations

from PyQt6.QtCore import QModelIndex, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QPushButton,
    QSpinBox,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from gui.models.dictionary_table_model import DictionaryTableModel, SortableProxyModel
from models.lexeme import DictionaryEntry
from utils.constants import DEFAULT_PAGE_SIZE


class DictionaryView(QWidget):
    """
    Table view for browsing dictionary entries with pagination.

    Signals:
        entry_selected: Emitted with the selected :class:`DictionaryEntry`.
    """

    entry_selected = pyqtSignal(object)  # DictionaryEntry | None
    generate_task_requested = pyqtSignal(list)  # list[str] of lexemes

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._all_entries: list[DictionaryEntry] = []
        self._page = 1
        self._page_size = DEFAULT_PAGE_SIZE
        self._total_pages = 1

        # --- Model ---
        self._source_model = DictionaryTableModel(self)
        self._proxy_model = SortableProxyModel(self)
        self._proxy_model.setSourceModel(self._source_model)

        # --- Table ---
        self._table = QTableView()
        self._table.setModel(self._proxy_model)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._table.setSortingEnabled(True)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive,
        )
        self._table.selectionModel().currentRowChanged.connect(self._on_row_changed)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._on_context_menu)

        # --- Pagination controls ---
        self._page_label = QLabel("Page 1 / 1")
        self._total_label = QLabel("0 entries")
        self._btn_prev = QPushButton("<")
        self._btn_prev.setFixedWidth(40)
        self._btn_prev.clicked.connect(self._prev_page)
        self._btn_next = QPushButton(">")
        self._btn_next.setFixedWidth(40)
        self._btn_next.clicked.connect(self._next_page)
        self._page_spin = QSpinBox()
        self._page_spin.setMinimum(1)
        self._page_spin.setMaximum(1)
        self._page_spin.valueChanged.connect(self._goto_page)

        pagination = QHBoxLayout()
        pagination.addWidget(self._total_label)
        pagination.addStretch()
        pagination.addWidget(self._btn_prev)
        pagination.addWidget(QLabel("Page"))
        pagination.addWidget(self._page_spin)
        pagination.addWidget(self._page_label)
        pagination.addWidget(self._btn_next)

        # --- Layout ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._table, stretch=1)
        layout.addLayout(pagination)

    # --- Public API ---

    def set_entries(self, entries: list[DictionaryEntry]) -> None:
        """Load entries into the view (paginated)."""
        self._all_entries = entries
        self._page = 1
        self._refresh()

    def set_page_size(self, size: int) -> None:
        self._page_size = max(10, size)
        self._page = 1
        self._refresh()

    def current_entry(self) -> DictionaryEntry | None:
        """Return the currently selected entry or ``None``."""
        index = self._table.currentIndex()
        if not index.isValid():
            return None
        source_index = self._proxy_model.mapToSource(index)
        return self._source_model.get_entry(source_index.row())

    def selected_entries(self) -> list[DictionaryEntry]:
        """Return all currently selected entries (supports multi-select)."""
        seen_rows: set[int] = set()
        entries: list[DictionaryEntry] = []
        for index in self._table.selectionModel().selectedRows():
            source_index = self._proxy_model.mapToSource(index)
            row = source_index.row()
            if row not in seen_rows:
                seen_rows.add(row)
                entry = self._source_model.get_entry(row)
                if entry is not None:
                    entries.append(entry)
        return entries

    # --- Internal ---

    def _refresh(self) -> None:
        total = len(self._all_entries)
        self._total_pages = max(1, (total + self._page_size - 1) // self._page_size)
        self._page = max(1, min(self._page, self._total_pages))

        start = (self._page - 1) * self._page_size
        end = start + self._page_size
        page_entries = self._all_entries[start:end]

        self._source_model.set_entries(page_entries)

        self._page_label.setText(f"/ {self._total_pages}")
        self._total_label.setText(f"{total} entries")
        self._page_spin.blockSignals(True)
        self._page_spin.setMaximum(self._total_pages)
        self._page_spin.setValue(self._page)
        self._page_spin.blockSignals(False)
        self._btn_prev.setEnabled(self._page > 1)
        self._btn_next.setEnabled(self._page < self._total_pages)

    def _prev_page(self) -> None:
        if self._page > 1:
            self._page -= 1
            self._refresh()

    def _next_page(self) -> None:
        if self._page < self._total_pages:
            self._page += 1
            self._refresh()

    def _goto_page(self, page: int) -> None:
        self._page = page
        self._refresh()

    def _on_context_menu(self, pos) -> None:  # pos: QPoint
        entries = self.selected_entries()
        if not entries:
            return
        menu = QMenu(self)
        action = menu.addAction("Generate Task…")
        if menu.exec(self._table.viewport().mapToGlobal(pos)) is action:
            self.generate_task_requested.emit(entries)

    def _on_row_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        if not current.isValid():
            self.entry_selected.emit(None)
            return
        source_index = self._proxy_model.mapToSource(current)
        entry = self._source_model.get_entry(source_index.row())
        self.entry_selected.emit(entry)
