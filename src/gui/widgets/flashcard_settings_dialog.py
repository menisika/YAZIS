"""Flashcard settings dialog."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config.settings import SettingsManager
from core.llm_service import LLMService
from utils.logging_config import get_logger

logger = get_logger("gui.flashcard_settings")


class FlashcardSettingsDialog(QDialog):
    """
    Settings dialog for Groq/LLM API configuration.

    Args:
        llm_service: For testing API connection.
        parent: Parent widget.

    """

    def __init__(
        self,
        llm_service: LLMService | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._llm_service = llm_service
        self.setWindowTitle("Flashcard Settings")
        self.setMinimumWidth(450)

        self._settings_mgr = SettingsManager()
        self._config = self._settings_mgr.settings.flashcard

        self._setup_ui()
        self._load_values()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # --- Groq API settings ---
        api_group = QGroupBox("Groq API (LLM)")
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
        self._api_key_edit.setText(self._config.groq_api_key)

    def _on_test_connection(self) -> None:
        key = self._api_key_edit.text().strip()
        if not key:
            self._test_label.setText("No API key entered.")
            return

        self._test_label.setText("Testing...")
        self._btn_test.setEnabled(False)

        if self._llm_service is None:
            self._llm_service = LLMService(api_key=key)
        else:
            self._llm_service.api_key = key

        ok = self._llm_service.test_connection()
        self._btn_test.setEnabled(True)

        if ok:
            self._test_label.setText("Connection successful!")
        else:
            self._test_label.setText("Connection failed.")

    def _on_save(self) -> None:
        self._settings_mgr.settings.flashcard.groq_api_key = (
            self._api_key_edit.text().strip()
        )

        try:
            self._settings_mgr.save()
        except Exception as exc:
            logger.warning("Failed to save settings: %s", exc)

        self.accept()
