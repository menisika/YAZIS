"""Настройка логирования приложения."""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

from utils.constants import APP_NAME, USER_DATA_DIR


def setup_logging(level: int = logging.INFO, log_dir: Path | None = None) -> None:
    """Настроить логирование для всего приложения.

    Аргументы:
        level: Корневой уровень логирования.
        log_dir: Каталог для лог-файлов. По умолчанию ~/.yazis/logs.
    """
    log_dir = log_dir or (USER_DATA_DIR / "logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "yazis.log"

    root_logger = logging.getLogger(APP_NAME)
    root_logger.setLevel(level)

    # Не добавлять дубликаты обработчиков при повторных вызовах
    if root_logger.handlers:
        return

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Обработчик консоли
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(fmt)
    root_logger.addHandler(console)

    # Ротируемый файловый обработчик (5 МБ, 3 резервные копии)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Получить дочерний логгер в пространстве имён приложения."""
    return logging.getLogger(f"{APP_NAME}.{name}")
