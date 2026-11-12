from __future__ import annotations

from typing import Final


class DistractionController:
    """Turns the whole body to one side and back: -1 left, 0 facing the soldier, 1 right."""

    TURN_SPEED: Final = 7.0
    MAX_SHIFT: Final = 4

    def __init__(self) -> None:
        self._facing = 0.0
        self._direction = 0
        self._until = -1.0

    @property
    def facing(self) -> float:
        return self._facing

    @property
    def direction(self) -> int:
        return self._direction

    @property
    def active(self) -> bool:
        return self._direction != 0

    @property
    def shift(self) -> int:
        """How many sprite pixels the face is displaced by the turn."""
        return round(self._facing * self.MAX_SHIFT)

    def distract(self, direction: int, until: float) -> None:
        self._direction = direction
        self._until = until

    def is_over(self, elapsed: float) -> bool:
        return self.active and elapsed >= self._until

    def stop(self) -> None:
        self._direction = 0
        self._until = -1.0

    def turn(self, dt: float) -> None:
        step = dt * self.TURN_SPEED
        self._facing += max(-step, min(step, self._direction - self._facing))
