from __future__ import annotations

from typing import Final

from ..random_source import RandomSource


class MouthController:
    """Flaps the mouth at random intervals while he talks."""

    MIN_FLAP: Final = 0.07
    MAX_FLAP: Final = 0.15

    def __init__(self, randomness: RandomSource) -> None:
        self._randomness = randomness
        self._open = False
        self._next_flap = 0.0

    @property
    def is_open(self) -> bool:
        return self._open

    def update(self, talking: bool, elapsed: float) -> None:
        if talking and elapsed >= self._next_flap:
            self._open = not self._open
            self._next_flap = elapsed + self._randomness.uniform(self.MIN_FLAP, self.MAX_FLAP)
        elif not talking:
            self._open = False
