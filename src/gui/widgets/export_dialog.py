"""Диалог экспорта: выбор формата, области и пути сохранения."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class ExportDialog(QDialog):
    """Диалог выбора формата экспорта, области и выходного пути.

    После exec() с результатом Accepted читать атрибуты selected_format и selected_path.
    """

    def __init__(
        self,
        total_entries: int,
        filtered_entries: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Export Dictionary")
        self.setMinimumWidth(450)

        self._total = total_entries
        self._filtered = filtered_entries
        self._selected_format: str = "json"
        self._selected_path: Path | None = None
        self._export_filtered: bool = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Выбор формата
        fmt_group = QGroupBox("Export Format")
        fmt_layout = QVBoxLayout(fmt_group)
        self._fmt_group = QButtonGroup(self)

        self._rb_json = QRadioButton("JSON")
        self._rb_json.setChecked(True)
        self._fmt_group.addButton(self._rb_json, 0)
        fmt_layout.addWidget(self._rb_json)

        self._rb_csv = QRadioButton("CSV")
        self._fmt_group.addButton(self._rb_csv, 1)
        fmt_layout.addWidget(self._rb_csv)

        self._rb_txt = QRadioButton("Plain Text (TXT)")
        self._fmt_group.addButton(self._rb_txt, 2)
        fmt_layout.addWidget(self._rb_txt)

        layout.addWidget(fmt_group)

        # Выбор области
        scope_group = QGroupBox("Scope")
        scope_layout = QVBoxLayout(scope_group)
        self._scope_group = QButtonGroup(self)

        self._rb_all = QRadioButton(f"All entries ({self._total})")
        self._rb_all.setChecked(True)
        self._scope_group.addButton(self._rb_all, 0)
        scope_layout.addWidget(self._rb_all)

        self._rb_filtered = QRadioButton(f"Filtered entries ({self._filtered})")
        self._scope_group.addButton(self._rb_filtered, 1)
        scope_layout.addWidget(self._rb_filtered)

        if self._filtered == self._total:
            self._rb_filtered.setEnabled(False)

        layout.addWidget(scope_group)

        # Путь
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Save to:"))
        self._path_edit = QLineEdit()
        self._path_edit.setReadOnly(True)
        path_layout.addWidget(self._path_edit, stretch=1)
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._on_browse)
        path_layout.addWidget(btn_browse)
        layout.addLayout(path_layout)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_export = QPushButton("Export")
        btn_export.clicked.connect(self._on_export)
        btn_layout.addWidget(btn_export)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    @property
    def selected_format(self) -> str:
        mapping = {0: "json", 1: "csv", 2: "txt"}
        return mapping.get(self._fmt_group.checkedId(), "json")

    @property
    def selected_path(self) -> Path | None:
        return self._selected_path

    @property
    def export_filtered(self) -> bool:
        return self._scope_group.checkedId() == 1

    def _on_browse(self) -> None:
        ext_map = {"json": "JSON Files (*.json)", "csv": "CSV Files (*.csv)", "txt": "Text Files (*.txt)"}
        fmt = self.selected_format
        filt = ext_map.get(fmt, "All Files (*)")
        path, _ = QFileDialog.getSaveFileName(self, "Export To", "", filt)
        if path:
            self._selected_path = Path(path)
            self._path_edit.setText(path)

    def _on_export(self) -> None:
        if self._selected_path is None:
            self._on_browse()
        if self._selected_path is not None:
            self.accept()
