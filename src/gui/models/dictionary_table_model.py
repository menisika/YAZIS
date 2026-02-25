"""Модель таблицы Qt для отображения записей словаря в QTableView."""

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush, QColor

from models.lexeme import DictionaryEntry

_COLUMNS = ("Lexeme", "POS", "Stem", "Frequency")


class DictionaryTableModel(QAbstractTableModel):
    """Только для чтения модель таблицы на списке DictionaryEntry.

    Колонки: Lexeme | POS | Stem | Frequency.
    """

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self._entries: list[DictionaryEntry] = []
        self._study_list_lexemes: frozenset[str] = frozenset()

    # Публичный API

    def set_study_list_lexemes(
        self, lexemes: set[str] | frozenset[str] | list[str]
    ) -> None:
        """Задать лексемы из списка изучения (для подсветки строк)."""
        self._study_list_lexemes = frozenset(x.lower() for x in lexemes)
        if self._entries:
            self.dataChanged.emit(
                self.index(0, 0),
                self.index(len(self._entries) - 1, self.columnCount() - 1),
            )

    def set_entries(self, entries: list[DictionaryEntry]) -> None:
        """Заменить все записи и обновить представление."""
        self.beginResetModel()
        self._entries = list(entries)
        self.endResetModel()

    def get_entry(self, row: int) -> DictionaryEntry | None:
        """Получить запись по индексу строки или None."""
        if 0 <= row < len(self._entries):
            return self._entries[row]
        return None

    def get_entry_by_index(self, index: QModelIndex) -> DictionaryEntry | None:
        """Получить запись по индексу модели."""
        if not index.isValid():
            return None
        return self.get_entry(index.row())

    # Переопределения QAbstractTableModel

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return len(self._entries)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return len(_COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        entry = self._entries[index.row()]
        if role == Qt.ItemDataRole.BackgroundRole:
            if entry.lexeme.lower() in self._study_list_lexemes:
                return QBrush(QColor(200, 220, 255))
            return None
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        col = index.column()
        if col == 0:
            return entry.lexeme
        if col == 1:
            return entry.pos.display_name()
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
    """Прокси-модель для сортировки таблицы словаря по колонкам."""

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:  # noqa: N802
        left_data = self.sourceModel().data(left, Qt.ItemDataRole.DisplayRole)
        right_data = self.sourceModel().data(right, Qt.ItemDataRole.DisplayRole)

        # Числовое сравнение для колонки частоты
        if left.column() == 3:
            return (left_data or 0) < (right_data or 0)

        # Строковое сравнение для остальных
        return str(left_data or "").lower() < str(right_data or "").lower()
