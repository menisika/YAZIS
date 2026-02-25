"""Виджет анимированной переворачивающейся карточки для изучения."""

from __future__ import annotations

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    Qt,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import QFont, QPainter, QPaintEvent
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from utils.constants import FLIP_SPEED_MS


class FlashcardWidget(QWidget):
    """Виджет карточки с анимацией горизонтального переворота.

    На карточке показывается текст лицевой стороны, после flip — оборотной.
    Анимация сжимает карточку по горизонтали до середины, меняет контент, затем разворачивает.

    Сигналы:
        flipped: По завершении анимации переворота.
    """

    flipped = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._front_text = ""
        self._back_text = ""
        self._is_flipped = False
        self._flip_progress: float = 0.0
        self._speed_key = "normal"

        self.setMinimumSize(400, 250)

        # Центральная подпись
        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setWordWrap(True)
        font = QFont()
        font.setPointSize(22)
        self._label.setFont(font)
        self._label.setStyleSheet(
            "QLabel {"
            "  background-color: white;"
            "  border: 3px solid #58cc02;"
            "  border-radius: 18px;"
            "  padding: 32px;"
            "  color: #333;"
            "}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(self._label)

        # Анимация переворота
        self._animation = QPropertyAnimation(self, b"flipProgress")
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animation.finished.connect(self._on_animation_finished)

    # Свойство Qt для анимации

    def _get_flip_progress(self) -> float:
        return self._flip_progress

    def _set_flip_progress(self, value: float) -> None:
        self._flip_progress = value
        # Масштабировать подпись по горизонтали в зависимости от прогресса
        if value <= 0.5:
            scale = 1.0 - 2.0 * value  # 1.0 -> 0.0
        else:
            scale = 2.0 * (value - 0.5)  # 0.0 -> 1.0

        # Поменять контент в середине
        if value >= 0.5 and not self._is_flipped:
            self._is_flipped = True
            self._label.setText(self._back_text)
        elif value < 0.5 and self._is_flipped:
            self._is_flipped = False
            self._label.setText(self._front_text)

        # Применить горизонтальное масштабирование через геометрию
        full_width = self.width() - 32  # account for margins
        scaled_width = max(1, int(full_width * scale))
        x_offset = (full_width - scaled_width) // 2 + 16
        self._label.setGeometry(
            x_offset,
            16,
            scaled_width,
            self.height() - 32,
        )

    flipProgress = pyqtProperty(float, _get_flip_progress, _set_flip_progress)

    # Публичный API

    def set_front(self, text: str) -> None:
        """Установить текст лицевой стороны карточки."""
        self._front_text = text
        if not self._is_flipped:
            self._label.setText(text)

    def set_back(self, text: str) -> None:
        """Установить текст оборотной стороны карточки."""
        self._back_text = text
        if self._is_flipped:
            self._label.setText(text)

    def set_speed(self, speed_key: str) -> None:
        """Задать скорость анимации переворота.

        Аргументы:
            speed_key: Одно из: slow, normal, fast.
        """
        self._speed_key = speed_key

    def flip(self) -> None:
        """Запустить анимацию переворота."""
        if self._animation.state() == QPropertyAnimation.State.Running:
            return
        duration = FLIP_SPEED_MS.get(self._speed_key, 350)
        self._animation.setDuration(duration)
        if self._is_flipped:
            self._animation.setStartValue(1.0)
            self._animation.setEndValue(0.0)
        else:
            self._animation.setStartValue(0.0)
            self._animation.setEndValue(1.0)
        self._animation.start()

    def reset(self) -> None:
        """Вернуть карточку на лицевую сторону без анимации."""
        self._animation.stop()
        self._is_flipped = False
        self._flip_progress = 0.0
        self._label.setText(self._front_text)
        # Восстановить полную геометрию
        self._label.setGeometry(
            16, 16, self.width() - 32, self.height() - 32
        )

    @property
    def is_flipped(self) -> bool:
        return self._is_flipped

    @property
    def is_animating(self) -> bool:
        return self._animation.state() == QPropertyAnimation.State.Running

    # Внутренние методы

    def _on_animation_finished(self) -> None:
        self.flipped.emit()

    def resizeEvent(self, event: object) -> None:  # noqa: N802
        """Поддерживать корректный размер подписи после изменения размера."""
        super().resizeEvent(event)  # type: ignore[arg-type]
        if not self._animation.state() == QPropertyAnimation.State.Running:
            self._label.setGeometry(
                16, 16, self.width() - 32, self.height() - 32
            )
