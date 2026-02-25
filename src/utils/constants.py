"""Константы приложения."""

from pathlib import Path

# Метаданные приложения
APP_NAME = "YAZIS"
APP_VERSION = "0.1.0"
APP_TITLE = "YAZIS — Natural Language Dictionary Formation System"

# Пути
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
RESOURCES_DIR = Path(__file__).resolve().parent.parent / "resources"
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "default_config.yaml"
USER_DATA_DIR = Path.home() / ".yazis"

# Фильтры файлов
DOCX_FILTER = "Word Documents (*.docx)"
DICT_JSON_FILTER = "JSON Dictionary (*.json)"
DICT_SQLITE_FILTER = "SQLite Dictionary (*.db)"
EXPORT_FILTERS = {
    "json": "JSON Files (*.json)",
    "csv": "CSV Files (*.csv)",
    "txt": "Text Files (*.txt)",
}

# Необходимые пакеты данных NLTK
NLTK_REQUIRED_DATA = [
    "punkt_tab",
    "averaged_perceptron_tagger_eng",
    "wordnet",
    "omw-1.4",
]

# Постраничный вывод
DEFAULT_PAGE_SIZE = 100

# Морфологические константы
VOWELS = frozenset("aeiou")
CONSONANTS = frozenset("bcdfghjklmnpqrstvwxyz")
SIBILANTS = frozenset(("s", "x", "z", "ch", "sh"))

# Константы карточек и изучения
STUDY_PROGRESS_PATH = USER_DATA_DIR / "study_progress.json"
SOUNDS_DIR = USER_DATA_DIR / "sounds"
MUSIC_DIR = Path(__file__).resolve().parent.parent / "data" / "music"
DEFAULT_CARDS_PER_SESSION = 20
FLIP_SPEED_MS = {"slow": 600, "normal": 350, "fast": 150}

DEFINITION_PROMPT_TEMPLATE = (
    "Provide a clear, concise definition for the English word '{word}' "
    "used as a {pos}. Only the definition, under 20 words. /no_think"
)
GROQ_MODEL = "qwen/qwen3-32b"
