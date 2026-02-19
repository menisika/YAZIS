"""Application-wide constants."""

from pathlib import Path

# Application metadata
APP_NAME = "YAZIS"
APP_VERSION = "0.1.0"
APP_TITLE = "YAZIS — Natural Language Dictionary Formation System"

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
RESOURCES_DIR = Path(__file__).resolve().parent.parent / "resources"
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "default_config.yaml"
USER_DATA_DIR = Path.home() / ".yazis"

# File filters
DOCUMENT_FILTER = "Supported Documents (*.docx *.txt *.pdf);;Word Documents (*.docx);;Text Files (*.txt);;PDF Documents (*.pdf);;All Files (*)"
DOCX_FILTER = "Word Documents (*.docx)"
DICT_JSON_FILTER = "JSON Dictionary (*.json)"
DICT_SQLITE_FILTER = "SQLite Dictionary (*.db)"
EXPORT_FILTERS = {
    "json": "JSON Files (*.json)",
    "csv": "CSV Files (*.csv)",
    "txt": "Text Files (*.txt)",
}

# NLTK required data packages
NLTK_REQUIRED_DATA = [
    "punkt_tab",
    "averaged_perceptron_tagger_eng",
    "wordnet",
    "omw-1.4",
]

# Pagination
DEFAULT_PAGE_SIZE = 100

# Morphological constants
VOWELS = frozenset("aeiou")
CONSONANTS = frozenset("bcdfghjklmnpqrstvwxyz")
SIBILANTS = frozenset(("s", "x", "z", "ch", "sh"))

# LLM (Groq) constants
GROQ_MODEL = "qwen/qwen3-32b"
