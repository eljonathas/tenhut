from __future__ import annotations

from collections.abc import Callable
from enum import Enum


class _Shapes:
    @staticmethod
    def square(phase: float) -> float:
        return 1.0 if phase < 0.5 else -1.0

    @staticmethod
    def triangle(phase: float) -> float:
        return 4 * phase - 1 if phase < 0.5 else 3 - 4 * phase


class Waveform(Enum):
    """Shape of one oscillator period: square for short arcade blips, triangle for the longer, softer jingles."""

    SQUARE = ("square", _Shapes.square)
    TRIANGLE = ("triangle", _Shapes.triangle)

    def __new__(cls, value: str, shape: Callable[[float], float]) -> Waveform:
        member = object.__new__(cls)
        member._value_ = value
        member._shape = shape
        return member

    def sample(self, phase: float) -> float:
        """Amplitude in -1..1 at ``phase`` (0..1) of the period."""
        return self._shape(phase)
