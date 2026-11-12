from __future__ import annotations

from typing import Final

from ..geometry import Point
from ..random_source import RandomSource
from .expression import Expression


class GazeController:
    """Where he looks: eases toward a target and picks a new one when idle."""

    EASING_SPEED: Final = 10.0
    FIRST_SCAN: Final = 1.0
    MIN_SCAN_INTERVAL: Final = 0.9
    MAX_SCAN_INTERVAL: Final = 2.6
    SIDE_GLANCE: Final = -0.3
    VIEWER_GLANCE: Final = Point(0.0, 0.2)
    VIEWER_GLANCE_HOLD: Final = 1.8

    def __init__(self, randomness: RandomSource) -> None:
        self._randomness = randomness
        self._look = Point(0.0, 0.0)
        self._target = Point(0.0, 0.0)
        self._next_scan = self.FIRST_SCAN
        self._squint = False

    @property
    def look(self) -> Point:
        return self._look

    @property
    def squinting(self) -> bool:
        return self._squint

    def look_aside(self, direction: int) -> None:
        self._target = Point(float(direction), self.SIDE_GLANCE)

    def look_at(self, target: Point) -> None:
        self._target = Point(*target)

    def look_at_viewer(self, elapsed: float) -> None:
        """Locks eyes with the soldier and squints at him for a moment."""
        self._target = self.VIEWER_GLANCE
        self._next_scan = elapsed + self.VIEWER_GLANCE_HOLD
        self._squint = True

    def fix(self, look: Point) -> None:
        """Parks the gaze exactly on ``look``."""
        self._look = look
        self._target = look

    def scan_is_due(self, elapsed: float) -> bool:
        return elapsed >= self._next_scan

    def scan(self, elapsed: float, expression: Expression) -> None:
        glance = expression.choose_glance(self._randomness)
        self._target = glance.target
        self._squint = glance.squint
        self._next_scan = elapsed + self._randomness.uniform(self.MIN_SCAN_INTERVAL, self.MAX_SCAN_INTERVAL)

    def ease(self, dt: float) -> None:
        fraction = min(1.0, dt * self.EASING_SPEED)
        self._look = Point(
            self._look.x + (self._target.x - self._look.x) * fraction,
            self._look.y + (self._target.y - self._look.y) * fraction,
        )
