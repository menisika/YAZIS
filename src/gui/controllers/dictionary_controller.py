"""Контроллер между DictionaryManager и виджетами GUI."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QFileDialog, QInputDialog, QMessageBox

from core.definition_service import DefinitionService
from core.dictionary_manager import DictionaryManager
from core.export_service import ExportService
from core.rule_engine import RuleEngine
from core.search_engine import SearchCriteria, SearchEngine
from core.sound_manager import SoundManager
from core.study_manager import StudyManager
from data.json_adapter import JSONAdapter
from data.sqlite_adapter import SQLiteAdapter
from gui.widgets.export_dialog import ExportDialog
from gui.widgets.word_form_dialog import WordFormDialog
from models.enums import PartOfSpeech
from models.lexeme import DictionaryEntry
from utils.exceptions import EntryNotFoundError, ExportError, PersistenceError
from utils.logging_config import get_logger

if TYPE_CHECKING:
    from gui.main_window import MainWindow

logger = get_logger("gui.dictionary_controller")


class DictionaryController:
    """
    Связывает DictionaryManager, движки поиска/экспорта и GUI.

    Обязанности:
    - Подключение сигналов/слотов между менеджером и представлениями.
    - Обработка запросов поиска с панели поиска.
    - Сохранение, загрузка, экспорт.
    - Отмена/повтор.
    - Жизненный цикл редактирования записей.
    """

    def __init__(
        self,
        manager: DictionaryManager,
        search_engine: SearchEngine,
        export_service: ExportService,
        rule_engine: RuleEngine,
        main_window: MainWindow,
        study_manager: StudyManager | None = None,
        definition_service: DefinitionService | None = None,
        sound_manager: SoundManager | None = None,
    ) -> None:
        self._manager = manager
        self._search = search_engine
        self._export = export_service
        self._rule_engine = rule_engine
        self._window = main_window
        self._study = study_manager
        self._def_service = definition_service
        self._sound = sound_manager

        # Текущее состояние поиска
        self._current_criteria = SearchCriteria()
        self._filtered_entries: list[DictionaryEntry] = []

        self._connect_signals()

    # Подключение сигналов

    def _connect_signals(self) -> None:
        # Менеджер -> интерфейс
        self._manager.dictionary_changed.connect(self._on_dictionary_changed)
        self._manager.dictionary_loaded.connect(self._on_dictionary_loaded)
        self._manager.dictionary_saved.connect(self._on_dictionary_saved)

        # Таблица словаря -> редактор
        self._window.dictionary_view.entry_selected.connect(self._on_entry_selected)

        # Редактор записи -> менеджер
        self._window.entry_editor.entry_saved.connect(self._on_entry_saved)

        # Панель поиска -> контроллер
        self._window.search_panel.search_requested.connect(self._on_search_requested)

        # Сигналы контекстного меню таблицы словаря
        self._window.dictionary_view.context_add_study.connect(
            self._on_context_add_study
        )
        self._window.dictionary_view.context_remove_study.connect(
            self._on_context_remove_study
        )
        self._window.dictionary_view.context_gen_definition.connect(
            self._on_context_gen_definition
        )

    # Обработчики изменений словаря

    def _update_status_counts(self) -> None:
        """Обновить счётчики лексем и списка изучения в строке состояния."""
        n = len(self._manager.dictionary)
        m = len(self._study.get_study_list()) if self._study else 0
        self._window.update_counts(n, m)

    def _on_dictionary_changed(self) -> None:
        """Обновить представление при изменении содержимого словаря."""
        self._refresh_view()
        self._update_status_counts()
        n = len(self._manager.dictionary)
        self._window.update_status(f"{n} lexemes loaded")

    def _on_dictionary_loaded(self) -> None:
        self._current_criteria = SearchCriteria()
        self._refresh_view()
        self._update_status_counts()
        path = self._manager.current_path
        self._window.update_status(
            f"Dictionary loaded from {path} — {len(self._manager.dictionary)} entries",
        )

    def _on_dictionary_saved(self) -> None:
        path = self._manager.current_path
        self._window.update_status(f"Dictionary saved to {path}")

    # Обновление представления

    def _refresh_view(self) -> None:
        """Применить текущие критерии поиска и обновить таблицу словаря."""
        result = self._search.search(
            self._manager.dictionary,
            self._current_criteria,
        )
        self._filtered_entries = result.entries
        # Все совпадения (не только текущая страница) для экспорта
        all_result = self._search.search(
            self._manager.dictionary,
            self._current_criteria,
            page_size=999_999,
        )
        self._filtered_entries = all_result.entries
        self._window.dictionary_view.set_entries(all_result.entries)
        self._refresh_study_list_highlight()

    def _refresh_study_list_highlight(self) -> None:
        """Обновить подсветку строк таблицы для списка изучения."""
        if self._study is not None:
            self._window.dictionary_view.set_study_list_lexemes(
                self._study.get_study_list()
            )
        else:
            self._window.dictionary_view.set_study_list_lexemes([])

    # Выбор и редактирование записи

    def _on_entry_selected(self, entry: DictionaryEntry | None) -> None:
        self._window.entry_editor.load_entry(entry)

    def _on_entry_saved(self, entry: DictionaryEntry) -> None:
        """Обработка сохранения из редактора записи."""
        try:
            if self._manager.dictionary.has_entry(entry.lexeme):
                self._manager.update_entry(entry)
            else:
                self._manager.add_entry(entry)
            logger.info("Entry saved: %s", entry.lexeme)
        except Exception as exc:
            QMessageBox.critical(
                self._window,
                "Error",
                f"Failed to save entry: {exc}",
            )

    # Поиск

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

    # Сохранение и загрузка

    def save_dictionary(self) -> None:
        """Сохранить по текущему пути или запросить путь."""
        if self._manager.current_path is None:
            self.save_dictionary_as()
            return
        try:
            self._manager.save()
        except (PersistenceError, RuntimeError) as exc:
            QMessageBox.critical(
                self._window,
                "Save Error",
                str(exc),
            )

    def save_dictionary_as(self, path: Path | None = None) -> None:
        """Сохранить по новому пути."""
        if path is None:
            path_str, _ = QFileDialog.getSaveFileName(
                self._window,
                "Save Dictionary As",
                "",
                "JSON Dictionary (*.json);;SQLite Dictionary (*.db)",
            )
            if not path_str:
                return
            path = Path(path_str)

        # Выбор адаптера по расширению
        if path.suffix.lower() == ".db":
            self._manager.repository = SQLiteAdapter()
        else:
            self._manager.repository = JSONAdapter()

        try:
            self._manager.save(path)
        except (PersistenceError, RuntimeError) as exc:
            QMessageBox.critical(
                self._window,
                "Save Error",
                str(exc),
            )

    def load_dictionary(self, path: Path) -> None:
        """Загрузить словарь с диска."""
        if path.suffix.lower() == ".db":
            self._manager.repository = SQLiteAdapter()
        else:
            self._manager.repository = JSONAdapter()
        try:
            self._manager.load(path)
        except (PersistenceError, RuntimeError) as exc:
            QMessageBox.critical(
                self._window,
                "Load Error",
                str(exc),
            )

    # Новый словарь

    def new_dictionary(self) -> None:
        self._manager.new_dictionary()

    # Отмена / Повтор

    def undo(self) -> None:
        self._manager.undo()

    def redo(self) -> None:
        self._manager.redo()

    # Добавление и удаление записи

    def add_new_entry(self) -> None:
        """Переключить редактор в режим новой записи."""
        lexeme, ok = QInputDialog.getText(
            self._window,
            "Add Entry",
            "Enter lexeme (base form):",
        )
        if ok and lexeme.strip():
            self._window.entry_editor.set_new_entry_mode(lexeme.strip())

    def delete_selected_entry(self) -> None:
        entry = self._window.dictionary_view.current_entry()
        if entry is None:
            QMessageBox.information(
                self._window,
                "Delete",
                "No entry selected.",
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

    # Экспорт

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

            entries = (
                self._filtered_entries
                if use_filtered
                else self._manager.dictionary.entries
            )
            try:
                self._export.export(entries, path, fmt)
                self._window.update_status(f"Exported {len(entries)} entries to {path}")
                QMessageBox.information(
                    self._window,
                    "Export Complete",
                    f"Successfully exported {len(entries)} entries to:\n{path}",
                )
            except ExportError as exc:
                QMessageBox.critical(
                    self._window,
                    "Export Error",
                    str(exc),
                )

    # Статистика

    def show_statistics(self) -> None:
        d = self._manager.dictionary
        total = len(d)
        pos_counts: dict[str, int] = {}
        for entry in d:
            pos_counts[entry.pos.display_name()] = pos_counts.get(entry.pos.display_name(), 0) + 1

        stats_lines = [f"Total entries: {total}", ""]
        study_count = len(self._study.get_study_list()) if self._study else 0
        stats_lines.append(f"В списке изучения: {study_count}")
        stats_lines.append("")
        stats_lines.append("By Part of Speech:")
        for pos, count in sorted(pos_counts.items(), key=lambda x: -x[1]):
            stats_lines.append(f"  {pos}: {count}")

        if d.metadata.source_documents:
            stats_lines.append("")
            stats_lines.append("Source documents:")
            for doc in d.metadata.source_documents:
                stats_lines.append(f"  - {doc}")

        QMessageBox.information(
            self._window,
            "Dictionary Statistics",
            "\n".join(stats_lines),
        )

    # Генерация словоформ

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

    # Изучение и карточки

    def _on_context_add_study(self, entry: DictionaryEntry) -> None:
        if not entry.definition.strip() and self._def_service and self._def_service.api_key:
            self._window.update_status(f"Fetching definition for '{entry.lexeme}'...")
            self._fetch_and_set_definition(entry)
        if self._study:
            self._study.add_to_study_list(entry.lexeme)
            self._window.update_status(f"Added '{entry.lexeme}' to study list")
        self._refresh_study_list_highlight()
        self._update_status_counts()

    def _on_context_remove_study(self, entry: DictionaryEntry) -> None:
        if self._study:
            self._study.remove_from_study_list(entry.lexeme)
            self._window.update_status(f"Removed '{entry.lexeme}' from study list")
        self._refresh_study_list_highlight()
        self._update_status_counts()

    def _on_context_gen_definition(self, entry: DictionaryEntry) -> None:
        self.generate_definition(entry)

    def _fetch_and_set_definition(self, entry: DictionaryEntry) -> bool:
        """Получить определение по API и обновить запись в менеджере. Возвращает True при успехе."""
        if self._def_service is None or not self._def_service.api_key:
            return False
        defn = self._def_service.fetch_definition(
            entry.lexeme, entry.pos.display_name()
        )
        if defn:
            entry.definition = defn
            try:
                self._manager.update_entry(entry)
            except Exception:
                pass
            self._window.entry_editor.load_entry(entry)
            return True
        return False

    def generate_definition(self, entry: DictionaryEntry) -> None:
        """Получить определение для одной записи через Groq API.

        Не добавляет запись в список изучения; только обновляет определение.
        """
        if self._def_service is None or not self._def_service.api_key:
            QMessageBox.information(
                self._window,
                "Definition",
                "Groq API key is not configured.\nGo to Study > Flashcard Settings.",
            )
            return
        self._window.update_status(f"Fetching definition for '{entry.lexeme}'...")
        if self._fetch_and_set_definition(entry):
            self._window.update_status(f"Definition set for '{entry.lexeme}'")
        else:
            self._window.update_status(
                f"Could not fetch definition for '{entry.lexeme}'"
            )

    def start_study_session(self, mode: str | None = None) -> None:
        """Запустить сессию изучения, при необходимости запросить режим."""
        from config.settings import SettingsManager
        from gui.widgets.study_session_dialog import StudySessionDialog

        if self._study is None:
            QMessageBox.information(
                self._window, "Study", "Study manager not available."
            )
            return

        entries = list(self._manager.dictionary)
        if not entries:
            QMessageBox.information(self._window, "Study", "Dictionary is empty.")
            return

        if mode is None:
            mode, ok = QInputDialog.getItem(
                self._window,
                "Study Mode",
                "Select study mode:",
                ["Word -> Definition", "Definition -> Word", "Word Form Practice"],
                editable=False,
            )
            if not ok:
                return
            mode_map = {
                "Word -> Definition": "word_to_def",
                "Definition -> Word": "def_to_word",
                "Word Form Practice": "word_form_practice",
            }
            mode = mode_map.get(mode, "word_to_def")

        cfg = SettingsManager().settings.flashcard
        cards = self._study.select_cards(
            entries, count=cfg.cards_per_session, mode=mode
        )
        if not cards:
            QMessageBox.information(
                self._window,
                "Study",
                "No cards available for this mode. (Entries may need definitions first.)",
            )
            return

        sound = self._sound or SoundManager(enabled=cfg.sound_enabled)
        sound.enabled = cfg.sound_enabled

        dlg = StudySessionDialog(
            entries=cards,
            mode=mode,
            study_manager=self._study,
            definition_service=self._def_service,
            sound_manager=sound,
            rule_engine=self._rule_engine,
            flip_speed=cfg.flip_speed,
            auto_advance=cfg.auto_advance,
            parent=self._window,
        )

        if (
            cfg.auto_fetch_definitions
            and self._def_service
            and self._def_service.api_key
        ):
            dlg.prefetch_definitions()

        dlg.exec()

    def show_edit_study_list(self) -> None:
        """Открыть диалог редактирования списка изучения; обновить подсветку при закрытии."""
        from gui.widgets.edit_study_list_dialog import EditStudyListDialog

        if self._study is None:
            QMessageBox.information(
                self._window, "Study List", "Study manager not available."
            )
            return
        dlg = EditStudyListDialog(self._study, parent=self._window)
        dlg.exec()
        self._refresh_view()
        self._update_status_counts()

    def show_flashcard_settings(self) -> None:
        """Открыть диалог настроек карточек."""
        from gui.widgets.flashcard_settings_dialog import FlashcardSettingsDialog

        dlg = FlashcardSettingsDialog(
            definition_service=self._def_service,
            parent=self._window,
        )
        if dlg.exec():
            # Применить настройки к сервисам
            from config.settings import SettingsManager

            cfg = SettingsManager().settings.flashcard
            if self._def_service:
                self._def_service.api_key = cfg.groq_api_key
            if self._sound:
                self._sound.enabled = cfg.sound_enabled
