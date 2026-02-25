"""Контекстный диалог справки с содержимым руководства пользователя."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


_HELP_HTML = """\
<h2>YAZIS User Guide</h2>

<h3>Getting Started</h3>
<p>YAZIS analyzes English documents and builds a dictionary of lexemes
(base word forms) with their morphological properties.</p>

<h3>Opening a Document</h3>
<ol>
  <li>Click <b>File &rarr; Open Document</b> or the <b>Open</b> toolbar button.</li>
  <li>Select a <b>.docx</b> file.</li>
  <li>The system will parse the document, extract tokens, and perform
      lexical and morphological analysis.</li>
  <li>Results appear in the dictionary table.</li>
</ol>

<h3>Browsing the Dictionary</h3>
<ul>
  <li>Click any column header to sort.</li>
  <li>Use pagination controls at the bottom to navigate large dictionaries.</li>
  <li>Click a row to view/edit its details in the right panel.</li>
</ul>

<h3>Editing Entries</h3>
<ul>
  <li>The right panel shows the selected entry's details.</li>
  <li>Edit the <b>Stem</b>, <b>POS</b>, <b>Frequency</b>, or <b>Notes</b>.</li>
  <li>Add or remove <b>Word Forms</b> in the table.</li>
  <li>Click <b>Save</b> to commit changes, or <b>Cancel</b> to revert.</li>
</ul>

<h3>Generating Word Forms</h3>
<ol>
  <li>Select a lexeme in the dictionary.</li>
  <li>Click <b>Tools &rarr; Generate Word Form</b> (Ctrl+G).</li>
  <li>Choose morphological parameters (tense, number, person, etc.).</li>
  <li>Click <b>Generate Form</b> for a specific form, or
      <b>Generate All Forms</b> for all standard inflections.</li>
</ol>

<h3>Searching and Filtering</h3>
<ul>
  <li>Use the <b>Search</b> bar to search by lexeme (supports wildcards
      <code>*</code> and <code>?</code>, or enable <b>Regex</b> mode).</li>
  <li>Filter by <b>POS</b> using the dropdown.</li>
  <li>Set <b>Frequency</b> range to limit results.</li>
  <li>Click <b>Clear</b> to reset all filters.</li>
</ul>

<h3>Saving and Loading</h3>
<ul>
  <li><b>File &rarr; Save Dictionary</b> (Ctrl+S) saves the current dictionary.</li>
  <li><b>File &rarr; Load Dictionary</b> (Ctrl+L) loads a previously saved dictionary.</li>
  <li>Supported formats: <b>JSON</b> (.json) and <b>SQLite</b> (.db).</li>
</ul>

<h3>Exporting</h3>
<ol>
  <li>Click <b>File &rarr; Export</b> (Ctrl+E).</li>
  <li>Choose format: JSON, CSV, or Plain Text.</li>
  <li>Choose scope: all entries or filtered subset.</li>
  <li>Select output file location.</li>
</ol>

<h3>Undo / Redo</h3>
<p>Use <b>Edit &rarr; Undo</b> (Ctrl+Z) and <b>Redo</b> (Ctrl+Shift+Z)
to reverse or re-apply dictionary edits.</p>

<h3>Keyboard Shortcuts</h3>
<table border="1" cellpadding="4">
  <tr><td><b>Ctrl+O</b></td><td>Open Document</td></tr>
  <tr><td><b>Ctrl+S</b></td><td>Save Dictionary</td></tr>
  <tr><td><b>Ctrl+L</b></td><td>Load Dictionary</td></tr>
  <tr><td><b>Ctrl+E</b></td><td>Export</td></tr>
  <tr><td><b>Ctrl+G</b></td><td>Generate Word Form</td></tr>
  <tr><td><b>Ctrl+Z</b></td><td>Undo</td></tr>
  <tr><td><b>Ctrl+Shift+Z</b></td><td>Redo</td></tr>
  <tr><td><b>Ctrl+N</b></td><td>New Dictionary</td></tr>
</table>
"""


class HelpDialog(QDialog):
    """Прокручиваемый HTML-диалог справки."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("YAZIS User Guide")
        self.resize(650, 550)

        layout = QVBoxLayout(self)
        browser = QTextBrowser()
        browser.setHtml(_HELP_HTML)
        browser.setOpenExternalLinks(True)
        layout.addWidget(browser, stretch=1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)
