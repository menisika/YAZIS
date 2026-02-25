"""Диалог настроек карточек."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from config.settings import FlashcardConfig, SettingsManager
from core.definition_service import DefinitionService
from utils.logging_config import get_logger

logger = get_logger("gui.flashcard_settings")


class FlashcardSettingsDialog(QDialog):
    """Диалог настроек изучения по карточкам.

    Аргументы:
        definition_service: Для проверки подключения к API.
        parent: Родительский виджет.
    """

    def __init__(
        self,
        definition_service: DefinitionService | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._def_service = definition_service
        self.setWindowTitle("Flashcard Settings")
        self.setMinimumWidth(450)

        self._settings_mgr = SettingsManager()
        self._config = self._settings_mgr.settings.flashcard

        self._setup_ui()
        self._load_values()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Настройки изучения
        study_group = QGroupBox("Study Settings")
        study_layout = QFormLayout(study_group)

        self._sound_check = QCheckBox("Enable sound effects")
        study_layout.addRow(self._sound_check)

        self._auto_advance_check = QCheckBox("Auto-advance after selection")
        study_layout.addRow(self._auto_advance_check)

        self._flip_speed_combo = QComboBox()
        self._flip_speed_combo.addItem("Slow", "slow")
        self._flip_speed_combo.addItem("Normal", "normal")
        self._flip_speed_combo.addItem("Fast", "fast")
        study_layout.addRow("Card flip speed:", self._flip_speed_combo)

        self._cards_spin = QSpinBox()
        self._cards_spin.setRange(5, 200)
        study_layout.addRow("Cards per session:", self._cards_spin)

        layout.addWidget(study_group)

        # Настройки Groq API
        api_group = QGroupBox("Definition Generation (Groq API)")
        api_layout = QFormLayout(api_group)

        self._api_key_edit = QLineEdit()
        self._api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key_edit.setPlaceholderText("Enter Groq API key...")
        api_layout.addRow("API Key:", self._api_key_edit)

        test_row = QHBoxLayout()
        self._btn_test = QPushButton("Test Connection")
        self._btn_test.clicked.connect(self._on_test_connection)
        test_row.addWidget(self._btn_test)
        self._test_label = QLabel("")
        test_row.addWidget(self._test_label)
        test_row.addStretch()
        api_layout.addRow(test_row)

        self._auto_fetch_check = QCheckBox("Auto-fetch definitions when starting study session")
        api_layout.addRow(self._auto_fetch_check)

        layout.addWidget(api_group)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self._on_save)
        btn_layout.addWidget(btn_save)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _load_values(self) -> None:
        c = self._config
        self._sound_check.setChecked(c.sound_enabled)
        self._auto_advance_check.setChecked(c.auto_advance)

        idx = self._flip_speed_combo.findData(c.flip_speed)
        if idx >= 0:
            self._flip_speed_combo.setCurrentIndex(idx)

        self._cards_spin.setValue(c.cards_per_session)
        self._api_key_edit.setText(c.groq_api_key)
        self._auto_fetch_check.setChecked(c.auto_fetch_definitions)

    def _on_test_connection(self) -> None:
        key = self._api_key_edit.text().strip()
        if not key:
            self._test_label.setText("No API key entered.")
            return

        self._test_label.setText("Testing...")
        self._btn_test.setEnabled(False)

        if self._def_service is None:
            self._def_service = DefinitionService(api_key=key)
        else:
            self._def_service.api_key = key

        ok = self._def_service.test_connection()
        self._btn_test.setEnabled(True)

        if ok:
            self._test_label.setText("Connection successful!")
        else:
            self._test_label.setText("Connection failed.")

    def _on_save(self) -> None:
        c = self._settings_mgr.settings.flashcard
        c.sound_enabled = self._sound_check.isChecked()
        c.auto_advance = self._auto_advance_check.isChecked()
        c.flip_speed = self._flip_speed_combo.currentData()
        c.cards_per_session = self._cards_spin.value()
        c.groq_api_key = self._api_key_edit.text().strip()
        c.auto_fetch_definitions = self._auto_fetch_check.isChecked()

        try:
            self._settings_mgr.save()
        except Exception as exc:
            logger.warning("Failed to save settings: %s", exc)

        self.accept()
