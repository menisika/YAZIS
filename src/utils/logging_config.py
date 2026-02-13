"""Logging configuration for the application."""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

from utils.constants import APP_NAME, USER_DATA_DIR


def setup_logging(level: int = logging.INFO, log_dir: Path | None = None) -> None:
    """Configure application-wide logging.

    Args:
        level: Root log level.
        log_dir: Directory for log files. Defaults to ~/.yazis/logs.
    """
    log_dir = log_dir or (USER_DATA_DIR / "logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "yazis.log"

    root_logger = logging.getLogger(APP_NAME)
    root_logger.setLevel(level)

    # Avoid adding duplicate handlers on repeated calls
    if root_logger.handlers:
        return

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(fmt)
    root_logger.addHandler(console)

    # Rotating file handler (5 MB, keep 3 backups)
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
    """Get a child logger under the application namespace."""
    return logging.getLogger(f"{APP_NAME}.{name}")
