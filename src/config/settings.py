"""Configuration manager: load/save YAML config with defaults."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from utils.constants import DEFAULT_CONFIG_PATH, DEFAULT_PAGE_SIZE, USER_DATA_DIR
from utils.exceptions import ConfigurationError
from utils.logging_config import get_logger

logger = get_logger("config.settings")


@dataclass
class StorageConfig:
    backend: str = "json"  # json | sqlite
    default_path: str = ""


@dataclass
class NLPConfig:
    strategy: str = "nltk"  # nltk | spacy
    spacy_model: str = "en_core_web_sm"
    stemmer: str = "snowball"  # porter | snowball


@dataclass
class UIConfig:
    page_size: int = DEFAULT_PAGE_SIZE
    theme: str = "system"  # system | light | dark
    window_width: int = 1280
    window_height: int = 800


@dataclass
class LoggingConfig:
    level: str = "INFO"


@dataclass
class FlashcardConfig:
    groq_api_key: str = ""


@dataclass
class AppSettings:
    """Top-level application settings."""

    storage: StorageConfig = field(default_factory=StorageConfig)
    nlp: NLPConfig = field(default_factory=NLPConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    flashcard: FlashcardConfig = field(default_factory=FlashcardConfig)


class SettingsManager:
    """Singleton configuration manager.

    Loads settings from YAML files, merging with defaults.
    Persists user overrides to ``~/.yazis/config.yaml``.
    """

    _instance: SettingsManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> SettingsManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._settings = AppSettings()
        self._user_config_path = USER_DATA_DIR / "config.yaml"
        self._initialized = True

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    @property
    def settings(self) -> AppSettings:
        return self._settings

    def load(self) -> AppSettings:
        """Load settings from default config, then overlay user config.

        Returns:
            Merged :class:`AppSettings`.
        """
        # Start with defaults
        self._settings = AppSettings()

        # Load bundled defaults
        if DEFAULT_CONFIG_PATH.exists():
            self._merge_from_yaml(DEFAULT_CONFIG_PATH)

        # Overlay user overrides
        if self._user_config_path.exists():
            self._merge_from_yaml(self._user_config_path)

        logger.info(
            "Settings loaded (backend=%s, nlp=%s)",
            self._settings.storage.backend,
            self._settings.nlp.strategy,
        )
        return self._settings

    def save(self) -> None:
        """Persist current settings to user config file."""
        try:
            self._user_config_path.parent.mkdir(parents=True, exist_ok=True)
            data = self._to_dict()
            with open(self._user_config_path, "w", encoding="utf-8") as fh:
                yaml.dump(data, fh, default_flow_style=False, sort_keys=False)
            logger.info("Settings saved to %s", self._user_config_path)
        except OSError as exc:
            raise ConfigurationError(f"Failed to save settings: {exc}") from exc

    def _merge_from_yaml(self, path: Path) -> None:
        """Merge settings from a YAML file into current settings."""
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
        except (OSError, yaml.YAMLError) as exc:
            logger.warning("Could not load config from %s: %s", path, exc)
            return

        if not isinstance(data, dict):
            return

        # Storage
        if "storage" in data:
            s = data["storage"]
            if isinstance(s, dict):
                self._settings.storage.backend = s.get(
                    "backend", self._settings.storage.backend
                )
                self._settings.storage.default_path = s.get(
                    "default_path", self._settings.storage.default_path
                )

        # NLP
        if "nlp" in data:
            n = data["nlp"]
            if isinstance(n, dict):
                self._settings.nlp.strategy = n.get(
                    "strategy", self._settings.nlp.strategy
                )
                self._settings.nlp.spacy_model = n.get(
                    "spacy_model", self._settings.nlp.spacy_model
                )
                self._settings.nlp.stemmer = n.get(
                    "stemmer", self._settings.nlp.stemmer
                )

        # UI
        if "ui" in data:
            u = data["ui"]
            if isinstance(u, dict):
                self._settings.ui.page_size = u.get(
                    "page_size", self._settings.ui.page_size
                )
                self._settings.ui.theme = u.get("theme", self._settings.ui.theme)
                self._settings.ui.window_width = u.get(
                    "window_width", self._settings.ui.window_width
                )
                self._settings.ui.window_height = u.get(
                    "window_height", self._settings.ui.window_height
                )

        # Logging
        if "logging" in data:
            lg = data["logging"]
            if isinstance(lg, dict):
                self._settings.logging.level = lg.get(
                    "level", self._settings.logging.level
                )

        # Flashcard (Groq/LLM)
        if "flashcard" in data:
            fc = data["flashcard"]
            if isinstance(fc, dict):
                self._settings.flashcard.groq_api_key = fc.get(
                    "groq_api_key", self._settings.flashcard.groq_api_key
                )

    def _to_dict(self) -> dict[str, Any]:
        s = self._settings
        return {
            "storage": {
                "backend": s.storage.backend,
                "default_path": s.storage.default_path,
            },
            "nlp": {
                "strategy": s.nlp.strategy,
                "spacy_model": s.nlp.spacy_model,
                "stemmer": s.nlp.stemmer,
            },
            "ui": {
                "page_size": s.ui.page_size,
                "theme": s.ui.theme,
                "window_width": s.ui.window_width,
                "window_height": s.ui.window_height,
            },
            "logging": {"level": s.logging.level},
            "flashcard": {
                "groq_api_key": s.flashcard.groq_api_key,
            },
        }
