"""
Application entry point.

Initializes configuration, logging, NLTK data, dependency injection,
and launches the PyQt6 GUI.
"""

from __future__ import annotations

import logging
import sys

from PyQt6.QtWidgets import QApplication


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
    from core.dictionary_manager import DictionaryManager
    from core.export_service import ExportService
    from core.lexical_analyzer import LexicalAnalyzer
    from core.morphological_analyzer import (
        MorphologicalAnalyzer,
        NLTKStrategy,
        SpaCyStrategy,
    )
    from core.rule_engine import RuleEngine
    from core.search_engine import SearchEngine
    from core.stem_extractor import StemExtractor
    from data.json_adapter import JSONAdapter
    from data.sqlite_adapter import SQLiteAdapter

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

    manager = DictionaryManager(repository=repository)

    # Services
    search_engine = SearchEngine()
    export_service = ExportService()

    # LLM (Groq) service
    import os

    from core.llm_service import LLMService

    groq_key = os.environ.get("GROQ_API_KEY", settings.flashcard.groq_api_key)
    llm_service = LLMService(api_key=groq_key)

    # --- GUI ---
    from gui.controllers.dictionary_controller import DictionaryController
    from gui.controllers.document_controller import DocumentController
    from gui.main_window import MainWindow

    window = MainWindow()
    window.resize(settings.ui.window_width, settings.ui.window_height)

    # Pink / yellow / white theme with larger type
    app.setStyleSheet("""
        * { font-family: "Georgia", "Trebuchet MS", serif; font-size: 16px; }
        QMainWindow, QDialog { background: #fef7f9; }
        QMenuBar { background: #ec4899; color: white; font-weight: 600; padding: 4px; font-size: 16px; }
        QMenuBar::item:selected { background: #fbbf24; border-radius: 6px; color: #333; }
        QMenu { background: white; border: 1px solid #fbcfe8; border-radius: 8px; }
        QMenu::item:selected { background: #fef3c7; color: #333; }
        QToolBar { background: #ffffff; border-bottom: 1px solid #fbcfe8; spacing: 8px; padding: 6px; }
        QPushButton {
            background: #ec4899; color: #ffffff; border: none; border-radius: 12px;
            padding: 10px 20px; font-size: 17px; font-weight: 700;
        }
        QPushButton:hover { background: #fbbf24; color: #333; }
        QPushButton:pressed { background: #db2777; color: white; }
        QPushButton:disabled { background: #fbcfe8; color: #9ca3af; }
        QGroupBox {
            font-weight: 600; border: 1px solid #fbcfe8; border-radius: 10px;
            margin-top: 12px; padding-top: 16px; background: white; font-size: 16px;
        }
        QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #4b4b4b; }
        QTableView {
            background: white; alternate-background-color: #fffbeb;
            gridline-color: #fde68a; border: 1px solid #fbcfe8; border-radius: 10px;
            selection-background-color: #fef3c7; selection-color: #333;
        }
        QHeaderView::section {
            background: #ec4899; color: white; font-weight: 600;
            padding: 8px; border: none; font-size: 16px;
        }
        QLineEdit, QSpinBox, QComboBox, QTextEdit {
            border: 2px solid #fbcfe8; border-radius: 10px; padding: 6px 10px; background: white; font-size: 16px;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {
            border-color: #ec4899;
        }
        QStatusBar { background: #ffffff; border-top: 1px solid #fbcfe8; color: #666; font-size: 15px; }
        QProgressBar { border: 1px solid #fbcfe8; border-radius: 8px; text-align: center; }
        QProgressBar::chunk { background: #ec4899; border-radius: 6px; }
    """)

    # Controllers
    dict_controller = DictionaryController(
        manager=manager,
        search_engine=search_engine,
        export_service=export_service,
        rule_engine=rule_engine,
        main_window=window,
        llm_service=llm_service,
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
