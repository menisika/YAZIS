"""Sound manager: programmatic WAV generation and QSoundEffect playback."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

from utils.constants import SOUNDS_DIR
from utils.logging_config import get_logger

logger = get_logger("core.sound_manager")

# WAV parameters
_SAMPLE_RATE = 22050
_SAMPLE_WIDTH = 2  # 16-bit
_CHANNELS = 1
_MAX_AMP = 32767


def _generate_tone(frequency: float, duration: float, volume: float = 0.5) -> bytes:
    """Generate a sine wave tone as raw PCM bytes."""
    n_samples = int(_SAMPLE_RATE * duration)
    samples = []
    for i in range(n_samples):
        t = i / _SAMPLE_RATE
        # Apply fade-in/fade-out envelope
        envelope = 1.0
        fade = int(0.01 * _SAMPLE_RATE)
        if i < fade:
            envelope = i / fade
        elif i > n_samples - fade:
            envelope = (n_samples - i) / fade
        value = volume * envelope * math.sin(2 * math.pi * frequency * t)
        samples.append(int(value * _MAX_AMP))
    return struct.pack(f"<{len(samples)}h", *samples)


def _generate_ding() -> bytes:
    """Ascending two-note 'ding' for correct answer."""
    tone1 = _generate_tone(880, 0.1, 0.4)   # A5
    tone2 = _generate_tone(1320, 0.15, 0.4)  # E6
    return tone1 + tone2


def _generate_whoosh() -> bytes:
    """Brief noise sweep for card flip."""
    n_samples = int(_SAMPLE_RATE * 0.2)
    samples = []
    import random as _rand
    rng = _rand.Random(42)  # deterministic
    for i in range(n_samples):
        envelope = 1.0
        fade = int(0.03 * _SAMPLE_RATE)
        if i < fade:
            envelope = i / fade
        elif i > n_samples - fade:
            envelope = (n_samples - i) / fade
        # Filtered noise
        noise = rng.uniform(-1.0, 1.0)
        freq_sweep = 200 + 800 * (i / n_samples)
        t = i / _SAMPLE_RATE
        modulated = noise * 0.3 * envelope * math.sin(2 * math.pi * freq_sweep * t)
        samples.append(int(modulated * _MAX_AMP))
    return struct.pack(f"<{len(samples)}h", *samples)


def _generate_tada() -> bytes:
    """Celebratory chord for session completion."""
    duration = 0.4
    n_samples = int(_SAMPLE_RATE * duration)
    # C major chord: C5, E5, G5
    freqs = [523.25, 659.25, 783.99]
    samples = []
    for i in range(n_samples):
        t = i / _SAMPLE_RATE
        envelope = 1.0
        fade = int(0.05 * _SAMPLE_RATE)
        if i < fade:
            envelope = i / fade
        elif i > n_samples - fade:
            envelope = (n_samples - i) / fade
        value = sum(math.sin(2 * math.pi * f * t) for f in freqs) / len(freqs)
        samples.append(int(0.4 * envelope * value * _MAX_AMP))
    return struct.pack(f"<{len(samples)}h", *samples)


def _write_wav(path: Path, pcm_data: bytes) -> None:
    """Write raw PCM data to a WAV file."""
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(_CHANNELS)
        wf.setsampwidth(_SAMPLE_WIDTH)
        wf.setframerate(_SAMPLE_RATE)
        wf.writeframes(pcm_data)


class SoundManager:
    """Manages sound effect playback using QSoundEffect.

    Generates WAV files on first use and plays them non-blocking.

    Args:
        enabled: Whether sounds are enabled initially.
    """

    def __init__(self, enabled: bool = True) -> None:
        self._enabled = enabled
        self._effects: dict[str, object] = {}
        self._sounds_ready = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    def ensure_sounds(self) -> None:
        """Generate WAV files if they don't exist."""
        if self._sounds_ready:
            return
        SOUNDS_DIR.mkdir(parents=True, exist_ok=True)

        generators = {
            "ding": _generate_ding,
            "whoosh": _generate_whoosh,
            "tada": _generate_tada,
        }
        for name, gen_fn in generators.items():
            path = SOUNDS_DIR / f"{name}.wav"
            if not path.exists():
                _write_wav(path, gen_fn())
                logger.debug("Generated sound file: %s", path)

        self._sounds_ready = True

    def play(self, name: str) -> None:
        """Play a sound effect by name (non-blocking).

        Args:
            name: One of ``ding``, ``whoosh``, ``tada``.
        """
        if not self._enabled:
            return

        self.ensure_sounds()
        wav_path = SOUNDS_DIR / f"{name}.wav"
        if not wav_path.exists():
            logger.warning("Sound file not found: %s", wav_path)
            return

        try:
            from PyQt6.QtCore import QUrl
            from PyQt6.QtMultimedia import QSoundEffect

            # Re-use or create QSoundEffect instances
            if name not in self._effects:
                effect = QSoundEffect()
                effect.setSource(QUrl.fromLocalFile(str(wav_path)))
                effect.setVolume(0.7)
                self._effects[name] = effect

            effect = self._effects[name]
            effect.play()  # type: ignore[union-attr]
        except ImportError:
            logger.debug("QtMultimedia not available, sound playback skipped")
        except Exception as exc:
            logger.debug("Sound playback error for '%s': %s", name, exc)
