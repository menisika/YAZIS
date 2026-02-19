"""Controller mediating between the DictionaryManager and GUI widgets."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QFileDialog, QInputDialog, QMessageBox

from core.dictionary_manager import DictionaryManager
from core.export_service import ExportService
from core.llm_service import LLMService
from core.rule_engine import RuleEngine
from core.search_engine import SearchCriteria, SearchEngine
from data.json_adapter import JSONAdapter
from data.sqlite_adapter import SQLiteAdapter
from gui.widgets.export_dialog import ExportDialog
from gui.widgets.word_form_dialog import WordFormDialog
from models.enums import PartOfSpeech
from models.lexeme import DictionaryEntry
from utils.exceptions import EntryNotFoundError, PersistenceError, ExportError
from utils.logging_config import get_logger

if TYPE_CHECKING:
    from gui.main_window import MainWindow

logger = get_logger("gui.dictionary_controller")


class DictionaryController:
    """Mediates between :class:`DictionaryManager`, search/export engines, and GUI.

    Responsibilities:
    - Wire signals/slots between manager and views.
    - Handle search requests from the search panel.
    - Handle save/load/export.
    - Handle undo/redo.
    - Handle entry editing lifecycle.
    """

    def __init__(
        self,
        manager: DictionaryManager,
        search_engine: SearchEngine,
        export_service: ExportService,
        rule_engine: RuleEngine,
        main_window: MainWindow,
        llm_service: LLMService | None = None,
    ) -> None:
        self._manager = manager
        self._search = search_engine
        self._export = export_service
        self._rule_engine = rule_engine
        self._window = main_window
        self._llm_service = llm_service

        # Current search state
        self._current_criteria = SearchCriteria()
        self._filtered_entries: list[DictionaryEntry] = []

        self._connect_signals()

    # --- Signal wiring ---

    def _connect_signals(self) -> None:
        # Manager -> UI
        self._manager.dictionary_changed.connect(self._on_dictionary_changed)
        self._manager.dictionary_loaded.connect(self._on_dictionary_loaded)
        self._manager.dictionary_saved.connect(self._on_dictionary_saved)

        # Dictionary view -> editor
        self._window.dictionary_view.entry_selected.connect(self._on_entry_selected)

        # Entry editor -> manager
        self._window.entry_editor.entry_saved.connect(self._on_entry_saved)

        # Search panel -> controller
        self._window.search_panel.search_requested.connect(self._on_search_requested)

        # Dictionary view context menu -> task generator
        self._window.dictionary_view.generate_task_requested.connect(
            self._on_generate_task_requested
        )


    # --- Dictionary change handlers ---

    def _on_dictionary_changed(self) -> None:
        """Refresh the view when the dictionary content changes."""
        self._refresh_view()
        n = len(self._manager.dictionary)
        self._window.update_status(f"{n} lexemes loaded")

    def _on_dictionary_loaded(self) -> None:
        self._current_criteria = SearchCriteria()
        self._refresh_view()
        path = self._manager.current_path
        self._window.update_status(
            f"Dictionary loaded from {path} — {len(self._manager.dictionary)} entries"
        )

    def _on_dictionary_saved(self) -> None:
        path = self._manager.current_path
        self._window.update_status(f"Dictionary saved to {path}")

    # --- View refresh ---

    def _refresh_view(self) -> None:
        """Apply current search criteria and update the dictionary view."""
        result = self._search.search(
            self._manager.dictionary, self._current_criteria
        )
        self._filtered_entries = result.entries
        # Get all matching (not just current page) for export scope
        all_result = self._search.search(
            self._manager.dictionary, self._current_criteria, page_size=999_999
        )
        self._filtered_entries = all_result.entries
        self._window.dictionary_view.set_entries(all_result.entries)

    # --- Entry selection / editing ---

    def _on_entry_selected(self, entry: DictionaryEntry | None) -> None:
        self._window.entry_editor.load_entry(entry)

    def _on_entry_saved(self, entry: DictionaryEntry) -> None:
        """Handle save from the entry editor."""
        try:
            if self._manager.dictionary.has_entry(entry.lexeme):
                self._manager.update_entry(entry)
            else:
                self._manager.add_entry(entry)
            logger.info("Entry saved: %s", entry.lexeme)
        except Exception as exc:
            QMessageBox.critical(
                self._window, "Error", f"Failed to save entry: {exc}"
            )

    # --- Search ---

    def _on_search_requested(
        self,
        query: str,
        pos_filter: PartOfSpeech | None,
        min_freq: int,
        max_freq: int,
        use_regex: bool,
    ) -> None:
        self._current_criteria = SearchCriteria(
            query=query,
            pos_filter=pos_filter,
            min_frequency=min_freq,
            max_frequency=max_freq,
            use_regex=use_regex,
        )
        self._refresh_view()

    # --- Save / Load ---

    def save_dictionary(self) -> None:
        """Save to the current path, or prompt for one."""
        if self._manager.current_path is None:
            self.save_dictionary_as()
            return
        try:
            self._manager.save()
        except (PersistenceError, RuntimeError) as exc:
            QMessageBox.critical(
                self._window, "Save Error", str(exc)
            )

    def save_dictionary_as(self, path: Path | None = None) -> None:
        """Save to a new path."""
        if path is None:
            path_str, _ = QFileDialog.getSaveFileName(
                self._window, "Save Dictionary As", "",
                "JSON Dictionary (*.json);;SQLite Dictionary (*.db)",
            )
            if not path_str:
                return
            path = Path(path_str)

        # Select adapter based on extension
        if path.suffix.lower() == ".db":
            self._manager.repository = SQLiteAdapter()
        else:
            self._manager.repository = JSONAdapter()

        try:
            self._manager.save(path)
        except (PersistenceError, RuntimeError) as exc:
            QMessageBox.critical(
                self._window, "Save Error", str(exc)
            )

    def load_dictionary(self, path: Path) -> None:
        """Load a dictionary from disk."""
        if path.suffix.lower() == ".db":
            self._manager.repository = SQLiteAdapter()
        else:
            self._manager.repository = JSONAdapter()
        try:
            self._manager.load(path)
        except (PersistenceError, RuntimeError) as exc:
            QMessageBox.critical(
                self._window, "Load Error", str(exc)
            )

    # --- New dictionary ---

    def new_dictionary(self) -> None:
        self._manager.new_dictionary()

    # --- Undo / Redo ---

    def undo(self) -> None:
        self._manager.undo()

    def redo(self) -> None:
        self._manager.redo()

    # --- Add / Delete entry ---

    def add_new_entry(self) -> None:
        """Switch editor to new-entry mode."""
        lexeme, ok = QInputDialog.getText(
            self._window, "Add Entry", "Enter lexeme (base form):"
        )
        if ok and lexeme.strip():
            self._window.entry_editor.set_new_entry_mode(lexeme.strip())

    def delete_selected_entry(self) -> None:
        entry = self._window.dictionary_view.current_entry()
        if entry is None:
            QMessageBox.information(
                self._window, "Delete", "No entry selected."
            )
            return
        reply = QMessageBox.question(
            self._window,
            "Delete Entry",
            f"Delete entry '{entry.lexeme}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self._manager.remove_entry(entry.lexeme)
                self._window.entry_editor.clear()
            except EntryNotFoundError:
                pass

    # --- Export ---

    def show_export_dialog(self) -> None:
        total = len(self._manager.dictionary)
        filtered = len(self._filtered_entries)
        dlg = ExportDialog(total, filtered, self._window)
        if dlg.exec():
            fmt = dlg.selected_format
            path = dlg.selected_path
            use_filtered = dlg.export_filtered

            if path is None:
                return

            entries = self._filtered_entries if use_filtered else self._manager.dictionary.entries
            try:
                self._export.export(entries, path, fmt)
                self._window.update_status(f"Exported {len(entries)} entries to {path}")
                QMessageBox.information(
                    self._window, "Export Complete",
                    f"Successfully exported {len(entries)} entries to:\n{path}",
                )
            except ExportError as exc:
                QMessageBox.critical(
                    self._window, "Export Error", str(exc)
                )

    # --- Statistics ---

    def show_statistics(self) -> None:
        d = self._manager.dictionary
        total = len(d)
        pos_counts: dict[str, int] = {}
        for entry in d:
            pos_counts[str(entry.pos)] = pos_counts.get(str(entry.pos), 0) + 1

        stats_lines = [f"Total entries: {total}", ""]
        stats_lines.append("By Part of Speech:")
        for pos, count in sorted(pos_counts.items(), key=lambda x: -x[1]):
            stats_lines.append(f"  {pos}: {count}")

        if d.metadata.source_documents:
            stats_lines.append("")
            stats_lines.append("Source documents:")
            for doc in d.metadata.source_documents:
                stats_lines.append(f"  - {doc}")

        QMessageBox.information(
            self._window, "Dictionary Statistics", "\n".join(stats_lines)
        )

    # --- Word form generation ---

    def show_generate_form_dialog(self) -> None:
        entry = self._window.dictionary_view.current_entry()
        if entry is None:
            QMessageBox.information(
                self._window,
                "Generate Form",
                "Please select a lexeme first.",
            )
            return
        dlg = WordFormDialog(entry, self._rule_engine, self._window)
        dlg.exec()

    # --- Task generation ---

    def _on_generate_task_requested(self, entries: list) -> None:
        """Handle the context-menu signal from DictionaryView."""
        self._open_task_dialog([(e.lexeme, str(e.pos)) for e in entries])

    def show_task_generator(self) -> None:
        """Open the task generator dialog (Study menu entry point)."""
        entries = self._window.dictionary_view.selected_entries()
        if not entries:
            QMessageBox.information(
                self._window,
                "Generate Task",
                "Please select one or more lexemes first.",
            )
            return
        self._open_task_dialog([(e.lexeme, str(e.pos)) for e in entries])

    def _open_task_dialog(self, word_pos_pairs: list) -> None:
        if self._llm_service is None or not self._llm_service.api_key:
            QMessageBox.warning(
                self._window,
                "Generate Task",
                "Groq API key is not configured.\n"
                "Please set it via Study → Flashcard Settings.",
            )
            return
        from gui.widgets.task_generator_dialog import TaskGeneratorDialog

        dlg = TaskGeneratorDialog(word_pos_pairs, self._llm_service, self._window)
        dlg.exec()

    # --- Flashcard / LLM settings ---

    def show_flashcard_settings(self) -> None:
        """Open the flashcard (Groq/LLM) settings dialog."""
        from gui.widgets.flashcard_settings_dialog import FlashcardSettingsDialog

        dlg = FlashcardSettingsDialog(
            llm_service=self._llm_service,
            parent=self._window,
        )
        if dlg.exec():
            from config.settings import SettingsManager
            cfg = SettingsManager().settings.flashcard
            if self._llm_service:
                self._llm_service.api_key = cfg.groq_api_key
