"""Main application window with menu bar, toolbar, status bar, and splitter layout."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from gui.widgets.dictionary_view import DictionaryView
from gui.widgets.entry_editor import EntryEditor
from gui.widgets.search_panel import SearchPanel
from utils.constants import APP_TITLE, DOCUMENT_FILTER

if TYPE_CHECKING:
    from gui.controllers.dictionary_controller import DictionaryController
    from gui.controllers.document_controller import DocumentController


class MainWindow(QMainWindow):
    """
    Application main window.

    Layout::

        ┌──────────────────────────────────────────────────┐
        │ Menu bar                                         │
        │ Toolbar                                          │
        ├──────────────────────┬───────────────────────────┤
        │ Search Panel         │                           │
        │ Dictionary View      │  Entry Editor             │
        │  (table, sortable)   │  (edit selected entry)    │
        ├──────────────────────┴───────────────────────────┤
        │ Status bar                                       │
        └──────────────────────────────────────────────────┘
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(900, 600)

        self._dict_controller: DictionaryController | None = None
        self._doc_controller: DocumentController | None = None

        # --- Widgets ---
        self.search_panel = SearchPanel()
        self.dictionary_view = DictionaryView()
        self.entry_editor = EntryEditor()

        # --- Layout ---
        self._setup_central_widget()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_status_bar()

    # --- Controller injection ---

    def set_controllers(
        self,
        dict_ctrl: DictionaryController,
        doc_ctrl: DocumentController,
    ) -> None:
        """Inject controllers after construction (avoids circular deps)."""
        self._dict_controller = dict_ctrl
        self._doc_controller = doc_ctrl

    # --- Layout setup ---

    def _setup_central_widget(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        # Left panel: search + dictionary view
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.search_panel)
        left_layout.addWidget(self.dictionary_view, stretch=1)

        # Splitter: left (dict) | right (editor)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(self.entry_editor)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.addWidget(splitter)

    def _setup_menu_bar(self) -> None:
        mb = self.menuBar()

        # --- File menu ---
        file_menu = mb.addMenu("&File")

        self.action_open = QAction("&Open Document...", self)
        self.action_open.setShortcut(QKeySequence.StandardKey.Open)
        self.action_open.triggered.connect(self._on_open_document)
        file_menu.addAction(self.action_open)

        file_menu.addSeparator()

        self.action_load_dict = QAction("&Load Dictionary...", self)
        self.action_load_dict.setShortcut(QKeySequence("Ctrl+L"))
        self.action_load_dict.triggered.connect(self._on_load_dictionary)
        file_menu.addAction(self.action_load_dict)

        self.action_save_dict = QAction("&Save Dictionary", self)
        self.action_save_dict.setShortcut(QKeySequence.StandardKey.Save)
        self.action_save_dict.triggered.connect(self._on_save_dictionary)
        file_menu.addAction(self.action_save_dict)

        self.action_save_as = QAction("Save Dictionary &As...", self)
        self.action_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.action_save_as.triggered.connect(self._on_save_as)
        file_menu.addAction(self.action_save_as)

        file_menu.addSeparator()

        self.action_export = QAction("E&xport...", self)
        self.action_export.setShortcut(QKeySequence("Ctrl+E"))
        self.action_export.triggered.connect(self._on_export)
        file_menu.addAction(self.action_export)

        file_menu.addSeparator()

        action_quit = QAction("&Quit", self)
        action_quit.setShortcut(QKeySequence.StandardKey.Quit)
        action_quit.triggered.connect(self.close)
        file_menu.addAction(action_quit)

        # --- Edit menu ---
        edit_menu = mb.addMenu("&Edit")

        self.action_undo = QAction("&Undo", self)
        self.action_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self.action_undo.triggered.connect(self._on_undo)
        edit_menu.addAction(self.action_undo)

        self.action_redo = QAction("&Redo", self)
        self.action_redo.setShortcut(QKeySequence.StandardKey.Redo)
        self.action_redo.triggered.connect(self._on_redo)
        edit_menu.addAction(self.action_redo)

        edit_menu.addSeparator()

        self.action_add_entry = QAction("&Add Entry...", self)
        self.action_add_entry.triggered.connect(self._on_add_entry)
        edit_menu.addAction(self.action_add_entry)

        self.action_delete_entry = QAction("&Delete Entry", self)
        self.action_delete_entry.setShortcut(QKeySequence.StandardKey.Delete)
        self.action_delete_entry.triggered.connect(self._on_delete_entry)
        edit_menu.addAction(self.action_delete_entry)

        # --- Dictionary menu ---
        dict_menu = mb.addMenu("&Dictionary")

        self.action_new_dict = QAction("&New Dictionary", self)
        self.action_new_dict.setShortcut(QKeySequence.StandardKey.New)
        self.action_new_dict.triggered.connect(self._on_new_dictionary)
        dict_menu.addAction(self.action_new_dict)

        dict_menu.addSeparator()

        self.action_stats = QAction("&Statistics", self)
        self.action_stats.triggered.connect(self._on_show_stats)
        dict_menu.addAction(self.action_stats)

        # --- Tools menu ---
        tools_menu = mb.addMenu("&Tools")

        self.action_generate = QAction("&Generate Word Form...", self)
        self.action_generate.setShortcut(QKeySequence("Ctrl+G"))
        self.action_generate.triggered.connect(self._on_generate_form)
        tools_menu.addAction(self.action_generate)

        # --- Study menu (LLM/Groq settings) ---
        study_menu = mb.addMenu("&Study")

        self.action_generate_task = QAction("&Generate Task...", self)
        self.action_generate_task.setShortcut(QKeySequence("Ctrl+T"))
        self.action_generate_task.triggered.connect(self._on_generate_task)
        study_menu.addAction(self.action_generate_task)

        study_menu.addSeparator()

        self.action_flashcard_settings = QAction("Flashcard &Settings...", self)
        self.action_flashcard_settings.triggered.connect(self._on_flashcard_settings)
        study_menu.addAction(self.action_flashcard_settings)

        # --- Help menu ---
        help_menu = mb.addMenu("&Help")

        self.action_help = QAction("&User Guide", self)
        self.action_help.setShortcut(QKeySequence.StandardKey.HelpContents)
        self.action_help.triggered.connect(self._on_help)
        help_menu.addAction(self.action_help)

        action_about = QAction("&About", self)
        action_about.triggered.connect(self._on_about)
        help_menu.addAction(action_about)

    def _setup_toolbar(self) -> None:
        tb = QToolBar("Main Toolbar")
        tb.setMovable(False)
        self.addToolBar(tb)

        tb.addAction(self.action_open)
        tb.addAction(self.action_save_dict)
        tb.addAction(self.action_export)
        tb.addSeparator()
        tb.addAction(self.action_undo)
        tb.addAction(self.action_redo)
        tb.addSeparator()
        tb.addAction(self.action_generate)

    def _setup_status_bar(self) -> None:
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self.update_status("Ready")

    # --- Public helpers ---

    def update_status(self, message: str) -> None:
        """Update the status bar text."""
        self._status_bar.showMessage(message)

    # --- Menu action handlers (delegate to controllers) ---

    def _on_open_document(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            "",
            DOCUMENT_FILTER,
        )
        if path and self._doc_controller:
            self._doc_controller.load_document(Path(path))

    def _on_load_dictionary(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Dictionary",
            "",
            "Dictionary Files (*.json *.db);;All Files (*)",
        )
        if path and self._dict_controller:
            self._dict_controller.load_dictionary(Path(path))

    def _on_save_dictionary(self) -> None:
        if self._dict_controller:
            self._dict_controller.save_dictionary()

    def _on_save_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Dictionary As",
            "",
            "JSON Dictionary (*.json);;SQLite Dictionary (*.db)",
        )
        if path and self._dict_controller:
            self._dict_controller.save_dictionary_as(Path(path))

    def _on_export(self) -> None:
        if self._dict_controller:
            self._dict_controller.show_export_dialog()

    def _on_undo(self) -> None:
        if self._dict_controller:
            self._dict_controller.undo()

    def _on_redo(self) -> None:
        if self._dict_controller:
            self._dict_controller.redo()

    def _on_add_entry(self) -> None:
        if self._dict_controller:
            self._dict_controller.add_new_entry()

    def _on_delete_entry(self) -> None:
        if self._dict_controller:
            self._dict_controller.delete_selected_entry()

    def _on_new_dictionary(self) -> None:
        if self._dict_controller:
            reply = QMessageBox.question(
                self,
                "New Dictionary",
                "Create a new empty dictionary? Unsaved changes will be lost.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._dict_controller.new_dictionary()

    def _on_show_stats(self) -> None:
        if self._dict_controller:
            self._dict_controller.show_statistics()

    def _on_generate_form(self) -> None:
        if self._dict_controller:
            self._dict_controller.show_generate_form_dialog()

    def _on_generate_task(self) -> None:
        if self._dict_controller:
            self._dict_controller.show_task_generator()

    def _on_flashcard_settings(self) -> None:
        if self._dict_controller:
            self._dict_controller.show_flashcard_settings()

    def _on_help(self) -> None:
        from gui.widgets.help_dialog import HelpDialog

        dlg = HelpDialog(self)
        dlg.exec()

    def _on_about(self) -> None:
        QMessageBox.about(
            self,
            "About YAZIS",
            "<h3>YAZIS</h3>"
            "<p>Natural Language Dictionary Formation System</p>"
            "<p>Version 0.1.0</p>"
            "<p>Lexical and lexico-grammatical analysis of English text.</p>",
        )
