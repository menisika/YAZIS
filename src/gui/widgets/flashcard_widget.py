"""Animated flip-card widget for flashcard study."""

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
    """A card widget with animated horizontal flip.

    The card displays *front* text and, after :meth:`flip`, displays
    *back* text.  The animation shrinks the card horizontally to its
    midpoint, swaps content, then expands back.

    Signals:
        flipped: Emitted after the flip animation completes.
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

        # Central label
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

        # Flip animation
        self._animation = QPropertyAnimation(self, b"flipProgress")
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animation.finished.connect(self._on_animation_finished)

    # --- Qt property for animation ---

    def _get_flip_progress(self) -> float:
        return self._flip_progress

    def _set_flip_progress(self, value: float) -> None:
        self._flip_progress = value
        # Scale the label horizontally based on progress
        if value <= 0.5:
            scale = 1.0 - 2.0 * value  # 1.0 -> 0.0
        else:
            scale = 2.0 * (value - 0.5)  # 0.0 -> 1.0

        # Swap content at the midpoint
        if value >= 0.5 and not self._is_flipped:
            self._is_flipped = True
            self._label.setText(self._back_text)
        elif value < 0.5 and self._is_flipped:
            self._is_flipped = False
            self._label.setText(self._front_text)

        # Apply horizontal scaling via geometry transform
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

    # --- Public API ---

    def set_front(self, text: str) -> None:
        """Set the front-of-card text."""
        self._front_text = text
        if not self._is_flipped:
            self._label.setText(text)

    def set_back(self, text: str) -> None:
        """Set the back-of-card text."""
        self._back_text = text
        if self._is_flipped:
            self._label.setText(text)

    def set_speed(self, speed_key: str) -> None:
        """Set the flip animation speed.

        Args:
            speed_key: One of ``slow``, ``normal``, ``fast``.
        """
        self._speed_key = speed_key

    def flip(self) -> None:
        """Start the flip animation."""
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
        """Reset the card to show the front without animation."""
        self._animation.stop()
        self._is_flipped = False
        self._flip_progress = 0.0
        self._label.setText(self._front_text)
        # Restore full geometry
        self._label.setGeometry(
            16, 16, self.width() - 32, self.height() - 32
        )

    @property
    def is_flipped(self) -> bool:
        return self._is_flipped

    @property
    def is_animating(self) -> bool:
        return self._animation.state() == QPropertyAnimation.State.Running

    # --- Internal ---

    def _on_animation_finished(self) -> None:
        self.flipped.emit()

    def resizeEvent(self, event: object) -> None:  # noqa: N802
        """Keep the label sized correctly after resize."""
        super().resizeEvent(event)  # type: ignore[arg-type]
        if not self._animation.state() == QPropertyAnimation.State.Running:
            self._label.setGeometry(
                16, 16, self.width() - 32, self.height() - 32
            )
