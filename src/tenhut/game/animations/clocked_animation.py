from __future__ import annotations

from abc import ABC

from tenhut.core import Clock

from .animation import Animation


class ClockedAnimation(Animation, ABC):
    """An animation timed by the wall clock, so a stalled loop cannot freeze it on screen."""

    def __init__(self, clock: Clock, duration: float) -> None:
        self._clock = clock
        self._duration = duration
        self._started_at = clock.now()

    @property
    def age(self) -> float:
        return self._clock.now() - self._started_at

    @property
    def finished(self) -> bool:
        return self.age > self._duration

    def update(self, dt: float) -> None:
        """Nothing to advance: the age comes from the clock."""
