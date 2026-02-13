"""Qt table model for displaying dictionary entries in a QTableView."""

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt

from models.lexeme import DictionaryEntry


_COLUMNS = ("Lexeme", "POS", "Stem", "Frequency")


class DictionaryTableModel(QAbstractTableModel):
    """Read-only table model backed by a list of :class:`DictionaryEntry`.

    Columns: Lexeme | POS | Stem | Frequency
    """

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self._entries: list[DictionaryEntry] = []

    # --- Public API ---

    def set_entries(self, entries: list[DictionaryEntry]) -> None:
        """Replace all entries and refresh the view."""
        self.beginResetModel()
        self._entries = list(entries)
        self.endResetModel()

    def get_entry(self, row: int) -> DictionaryEntry | None:
        """Get the entry at *row* index, or ``None``."""
        if 0 <= row < len(self._entries):
            return self._entries[row]
        return None

    def get_entry_by_index(self, index: QModelIndex) -> DictionaryEntry | None:
        """Get entry for a model index."""
        if not index.isValid():
            return None
        return self.get_entry(index.row())

    # --- QAbstractTableModel overrides ---

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return len(self._entries)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return len(_COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        entry = self._entries[index.row()]
        col = index.column()
        if col == 0:
            return entry.lexeme
        if col == 1:
            return str(entry.pos)
        if col == 2:
            return entry.stem
        if col == 3:
            return entry.frequency
        return None

    def headerData(  # noqa: N802
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal and 0 <= section < len(_COLUMNS):
            return _COLUMNS[section]
        if orientation == Qt.Orientation.Vertical:
            return section + 1
        return None


class SortableProxyModel(QSortFilterProxyModel):
    """Proxy that enables column-based sorting on the dictionary table."""

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:  # noqa: N802
        left_data = self.sourceModel().data(left, Qt.ItemDataRole.DisplayRole)
        right_data = self.sourceModel().data(right, Qt.ItemDataRole.DisplayRole)

        # Numeric comparison for frequency column
        if left.column() == 3:
            return (left_data or 0) < (right_data or 0)

        # String comparison for others
        return str(left_data or "").lower() < str(right_data or "").lower()
