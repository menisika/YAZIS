"""Application entry point.

Initializes configuration, logging, NLTK data, dependency injection,
and launches the PyQt6 GUI.
"""

from __future__ import annotations

import logging
import sys

from PyQt6.QtWidgets import QApplication, QMessageBox


def _ensure_nltk_data() -> None:
    """Download required NLTK data packages if missing."""
    import nltk  # type: ignore[import-untyped]
    from utils.constants import NLTK_REQUIRED_DATA

    for pkg in NLTK_REQUIRED_DATA:
        try:
            nltk.data.find(f"tokenizers/{pkg}" if "punkt" in pkg else pkg)
        except LookupError:
            nltk.download(pkg, quiet=True)


def main() -> None:
    """Application main function."""
    # Load .env from project root (cwd when run from repo) so API keys are available
    from dotenv import load_dotenv
    load_dotenv()

    # --- Qt application ---
    app = QApplication(sys.argv)
    app.setApplicationName("YAZIS")
    app.setApplicationVersion("0.1.0")

    # --- Configuration ---
    from config.settings import SettingsManager

    settings_mgr = SettingsManager()
    settings = settings_mgr.load()

    # --- Logging ---
    from utils.logging_config import setup_logging

    log_level = getattr(logging, settings.logging.level.upper(), logging.INFO)
    setup_logging(level=log_level)

    from utils.logging_config import get_logger
    logger = get_logger("main")
    logger.info("YAZIS starting up")

    # --- NLTK data ---
    try:
        _ensure_nltk_data()
    except Exception as exc:
        logger.warning("NLTK data download issue: %s", exc)

    # --- Core components ---
    from core.document_processor import DocumentProcessorFactory
    from core.lexical_analyzer import LexicalAnalyzer
    from core.morphological_analyzer import (
        MorphologicalAnalyzer,
        NLTKStrategy,
        SpaCyStrategy,
    )
    from core.stem_extractor import StemExtractor
    from core.rule_engine import RuleEngine
    from core.dictionary_manager import DictionaryManager
    from core.search_engine import SearchEngine
    from core.export_service import ExportService
    from data.json_adapter import JSONAdapter
    from data.sqlite_adapter import SQLiteAdapter

    # Register document processors
    DocumentProcessorFactory.register_defaults()

    # NLP components
    lexical_analyzer = LexicalAnalyzer()
    stem_extractor = StemExtractor(algorithm=settings.nlp.stemmer)
    rule_engine = RuleEngine()

    # Morphological analysis strategy
    if settings.nlp.strategy == "spacy":
        try:
            strategy = SpaCyStrategy(settings.nlp.spacy_model)
            # Trigger model load to verify
            strategy._load_model()
        except Exception as exc:
            logger.warning("spaCy unavailable, falling back to NLTK: %s", exc)
            strategy = NLTKStrategy()
    else:
        strategy = NLTKStrategy()

    morph_analyzer = MorphologicalAnalyzer(strategy=strategy)

    # Repository
    if settings.storage.backend == "sqlite":
        repository = SQLiteAdapter()
    else:
        repository = JSONAdapter()

    # Dictionary manager (Singleton)
    DictionaryManager.reset_instance()
    manager = DictionaryManager.get_instance(repository=repository)

    # Services
    search_engine = SearchEngine()
    export_service = ExportService()

    # Flashcard-related services
    from core.definition_service import DefinitionService
    from core.study_manager import StudyManager
    from core.sound_manager import SoundManager

    import os
    groq_key = os.environ.get("GROQ_API_KEY", settings.flashcard.groq_api_key)
    definition_service = DefinitionService(api_key=groq_key)
    study_manager = StudyManager()
    sound_manager = SoundManager(enabled=settings.flashcard.sound_enabled)

    # --- GUI ---
    from gui.main_window import MainWindow
    from gui.controllers.dictionary_controller import DictionaryController
    from gui.controllers.document_controller import DocumentController

    window = MainWindow()
    window.resize(settings.ui.window_width, settings.ui.window_height)

    # Duolingo-inspired minimalistic stylesheet
    app.setStyleSheet("""
        * { font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; }
        QMainWindow, QDialog { background: #f7f7f7; }
        QMenuBar { background: #58cc02; color: white; font-weight: 600; padding: 2px; }
        QMenuBar::item:selected { background: #46a302; border-radius: 4px; }
        QMenu { background: white; border: 1px solid #e0e0e0; border-radius: 6px; }
        QMenu::item:selected { background: #e6f9d4; color: #333; }
        QToolBar { background: #ffffff; border-bottom: 1px solid #e5e5e5; spacing: 6px; padding: 3px; }
        QPushButton {
            background: #58cc02; color: #ffffff; border: none; border-radius: 8px;
            padding: 8px 18px; font-size: 14px; font-weight: 700;
        }
        QPushButton:hover { background: #46a302; }
        QPushButton:pressed { background: #3b8c02; }
        QPushButton:disabled { background: #c8c8c8; color: #999; }
        QGroupBox {
            font-weight: 600; border: 1px solid #e0e0e0; border-radius: 10px;
            margin-top: 10px; padding-top: 14px; background: white;
        }
        QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px; color: #4b4b4b; }
        QTableView {
            background: white; alternate-background-color: #f0fce4;
            gridline-color: #e5e5e5; border: 1px solid #e0e0e0; border-radius: 8px;
            selection-background-color: #d4f5a8; selection-color: #333;
        }
        QHeaderView::section {
            background: #58cc02; color: white; font-weight: 600;
            padding: 5px; border: none;
        }
        QLineEdit, QSpinBox, QComboBox, QTextEdit {
            border: 2px solid #e0e0e0; border-radius: 8px; padding: 4px 8px; background: white;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {
            border-color: #58cc02;
        }
        QStatusBar { background: #ffffff; border-top: 1px solid #e5e5e5; color: #666; }
        QProgressBar { border: 1px solid #e0e0e0; border-radius: 6px; text-align: center; }
        QProgressBar::chunk { background: #58cc02; border-radius: 5px; }
    """)

    # Controllers
    dict_controller = DictionaryController(
        manager=manager,
        search_engine=search_engine,
        export_service=export_service,
        rule_engine=rule_engine,
        main_window=window,
        study_manager=study_manager,
        definition_service=definition_service,
        sound_manager=sound_manager,
    )
    doc_controller = DocumentController(
        manager=manager,
        lexical_analyzer=lexical_analyzer,
        morphological_analyzer=morph_analyzer,
        stem_extractor=stem_extractor,
        rule_engine=rule_engine,
        main_window=window,
    )

    window.set_controllers(dict_controller, doc_controller)

    # --- Show window ---
    window.show()
    logger.info("YAZIS ready")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
