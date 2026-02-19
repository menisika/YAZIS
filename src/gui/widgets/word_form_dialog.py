"""Dialog for generating inflected word forms from a lexeme."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.rule_engine import RuleEngine
from models.lexeme import DictionaryEntry, MorphologicalFeature, WordForm


class WordFormDialog(QDialog):
    """
    Dialog to generate word forms from a lexeme with selectable features.

    Args:
        entry: The dictionary entry to generate forms for.
        rule_engine: The rule engine to use for generation.
        parent: Parent widget.

    """

    def __init__(
        self,
        entry: DictionaryEntry,
        rule_engine: RuleEngine,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._entry = entry
        self._rule_engine = rule_engine
        self._generated_forms: list[WordForm] = []

        self.setWindowTitle(f"Generate Word Forms — {entry.lexeme}")
        self.setMinimumWidth(500)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Info
        info = QLabel(
            f"<b>Lexeme:</b> {self._entry.lexeme} &nbsp; "
            f"<b>POS:</b> {self._entry.pos.value} &nbsp; "
            f"<b>Stem:</b> {self._entry.stem}",
        )
        layout.addWidget(info)

        # Feature selectors
        feat_group = QGroupBox("Morphological Parameters")
        feat_layout = QFormLayout(feat_group)

        self._tense_combo = QComboBox()
        self._tense_combo.addItem("(any)", None)
        for t in [
            "present",
            "past",
            "past_participle",
            "present_participle",
            "infinitive",
        ]:
            self._tense_combo.addItem(t, t)
        feat_layout.addRow("Tense:", self._tense_combo)

        self._number_combo = QComboBox()
        self._number_combo.addItem("(any)", None)
        self._number_combo.addItem("singular", "singular")
        self._number_combo.addItem("plural", "plural")
        feat_layout.addRow("Number:", self._number_combo)

        self._person_combo = QComboBox()
        self._person_combo.addItem("(any)", None)
        self._person_combo.addItem("1st", "1st")
        self._person_combo.addItem("2nd", "2nd")
        self._person_combo.addItem("3rd", "3rd")
        feat_layout.addRow("Person:", self._person_combo)

        self._degree_combo = QComboBox()
        self._degree_combo.addItem("(any)", None)
        self._degree_combo.addItem("positive", "positive")
        self._degree_combo.addItem("comparative", "comparative")
        self._degree_combo.addItem("superlative", "superlative")
        feat_layout.addRow("Degree:", self._degree_combo)

        self._case_combo = QComboBox()
        self._case_combo.addItem("(any)", None)
        self._case_combo.addItem("possessive", "possessive")
        feat_layout.addRow("Case:", self._case_combo)

        layout.addWidget(feat_group)

        # Generate buttons
        btn_layout = QHBoxLayout()
        self._btn_generate_one = QPushButton("Generate Form")
        self._btn_generate_one.clicked.connect(self._on_generate_one)
        btn_layout.addWidget(self._btn_generate_one)

        self._btn_generate_all = QPushButton("Generate All Forms")
        self._btn_generate_all.clicked.connect(self._on_generate_all)
        btn_layout.addWidget(self._btn_generate_all)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Result display
        result_group = QGroupBox("Generated Forms")
        result_layout = QVBoxLayout(result_group)
        self._result_text = QTextEdit()
        self._result_text.setReadOnly(True)
        result_layout.addWidget(self._result_text)
        layout.addWidget(result_group, stretch=1)

        # Close
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    @property
    def generated_forms(self) -> list[WordForm]:
        return self._generated_forms

    def _build_features(self) -> MorphologicalFeature:
        return MorphologicalFeature(
            tense=self._tense_combo.currentData(),
            number=self._number_combo.currentData(),
            person=self._person_combo.currentData(),
            degree=self._degree_combo.currentData(),
            case=self._case_combo.currentData(),
        )

    def _on_generate_one(self) -> None:
        features = self._build_features()
        wf = self._rule_engine.generate_form(
            self._entry.lexeme,
            self._entry.pos,
            features,
        )
        self._generated_forms = [wf]
        self._display_forms([wf])

    def _on_generate_all(self) -> None:
        forms = self._rule_engine.generate_all_forms(
            self._entry.lexeme,
            self._entry.pos,
        )
        self._generated_forms = forms
        self._display_forms(forms)

    def _display_forms(self, forms: list[WordForm]) -> None:
        lines: list[str] = []
        for wf in forms:
            lines.append(
                f"  {wf.form:20s}  ending: {wf.ending:10s}  {wf.features.summary()}",
            )
        header = f"Lexeme: {self._entry.lexeme} ({self._entry.pos.value})\n"
        header += "-" * 60 + "\n"
        self._result_text.setPlainText(header + "\n".join(lines))
