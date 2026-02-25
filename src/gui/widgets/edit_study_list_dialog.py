"""Диалог просмотра и редактирования списка изучения (добавление/удаление слов)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from core.study_manager import StudyManager


class EditStudyListDialog(QDialog):
    """Показывает все слова списка изучения; пользователь может удалить выбранные."""

    def __init__(
        self,
        study_manager: StudyManager,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit Study List")
        self.setMinimumSize(400, 350)
        self._study = study_manager
        self._setup_ui()
        self._reload_list()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        self._list = QListWidget()
        self._list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout.addWidget(self._list)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._btn_remove = QPushButton("Remove selected")
        self._btn_remove.clicked.connect(self._on_remove_selected)
        btn_layout.addWidget(self._btn_remove)
        self._btn_close = QPushButton("Close")
        self._btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self._btn_close)
        layout.addLayout(btn_layout)

    def _reload_list(self) -> None:
        self._list.clear()
        for lexeme in sorted(self._study.get_study_list(), key=str.lower):
            self._list.addItem(QListWidgetItem(lexeme))
        self._btn_remove.setEnabled(self._list.count() > 0)

    def _on_remove_selected(self) -> None:
        rows = sorted(set(i.row() for i in self._list.selectedIndexes()), reverse=True)
        if not rows:
            return
        for row in rows:
            item = self._list.item(row)
            if item is not None:
                lexeme = item.text()
                self._study.remove_from_study_list(lexeme)
        self._reload_list()
