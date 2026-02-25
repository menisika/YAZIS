"""Менеджер звука: воспроизведение случайной музыки из папки data/music."""

from __future__ import annotations

import random
from pathlib import Path

from utils.constants import MUSIC_DIR
from utils.logging_config import get_logger

try:
    from PyQt6.QtCore import QUrl
    from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
except ImportError:
    QUrl = None  # type: ignore[misc, assignment]
    QAudioOutput = None  # type: ignore[misc, assignment]
    QMediaPlayer = None  # type: ignore[misc, assignment]

logger = get_logger("core.sound_manager")

_AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".flac"}


def _get_music_files() -> list[Path]:
    """Собрать все аудиофайлы из каталога музыки."""
    if not MUSIC_DIR.exists():
        return []
    return [
        f for f in MUSIC_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in _AUDIO_EXTENSIONS
    ]


class SoundManager:
    """Управление воспроизведением звука через QMediaPlayer.

    При каждом вызове play() воспроизводит случайный трек из src/data/music.

    Аргументы:
        enabled: Включён ли звук изначально.
    """

    def __init__(self, *, enabled: bool = True) -> None:
        self._enabled = enabled
        self._player: object | None = None
        self._output: object | None = None

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    def _ensure_player(self) -> bool:
        """Отложенная инициализация QMediaPlayer и QAudioOutput. Возвращает False при недоступности."""
        if self._player is not None:
            return True
        if QMediaPlayer is None or QAudioOutput is None or QUrl is None:
            logger.debug("QtMultimedia not available, sound playback skipped")
            return False
        try:
            self._player = QMediaPlayer()
            self._output = QAudioOutput()
            self._player.setAudioOutput(self._output)
            return True
        except (ImportError, TypeError) as exc:
            logger.debug("QtMultimedia init failed: %s", exc)
            return False

    def play(self, _name: str = "") -> None:
        """Воспроизвести случайный трек из папки музыки (неблокирующе).

        Аргументы:
            name: Игнорируется; оставлен для совместимости API (ding, whoosh, tada).
        """
        if not self._enabled:
            return

        files = _get_music_files()
        if not files:
            logger.warning("No audio files found in %s", MUSIC_DIR)
            return

        if not self._ensure_player() or self._player is None or self._output is None:
            return

        path = random.choice(files)
        try:
            self._player.setSource(QUrl.fromLocalFile(str(path)))
            self._output.setVolume(0.7)
            self._player.play()
        except (ImportError, OSError, ValueError) as exc:
            logger.debug("Sound playback error for '%s': %s", path, exc)
