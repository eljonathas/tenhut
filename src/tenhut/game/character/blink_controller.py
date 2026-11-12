from __future__ import annotations

import math
from typing import Final

from ..random_source import RandomSource


class BlinkController:
    """Closes the eyes for a split second every few seconds."""

    FIRST_BLINK: Final = 2.0
    BLINK_DURATION: Final = 0.13
    MIN_INTERVAL: Final = 2.2
    MAX_INTERVAL: Final = 5.0

    def __init__(self, randomness: RandomSource) -> None:
        self._randomness = randomness
        self._next_blink = self.FIRST_BLINK
        self._eyes_closed_until = -1.0

    def update(self, elapsed: float) -> None:
        if elapsed >= self._next_blink:
            self._eyes_closed_until = elapsed + self.BLINK_DURATION
            self._next_blink = elapsed + self._randomness.uniform(self.MIN_INTERVAL, self.MAX_INTERVAL)

    def is_blinking(self, elapsed: float) -> bool:
        return elapsed < self._eyes_closed_until

    def suppress(self) -> None:
        """Never blink again (for portraits)."""
        self._next_blink = math.inf
