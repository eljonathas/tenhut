from __future__ import annotations

from typing import NamedTuple


class Point(NamedTuple):
    """A 2D position or offset. A tuple subclass, so pygame draws with it directly."""

    x: float
    y: float

    def moved(self, dx: float = 0, dy: float = 0) -> Point:
        return Point(self.x + dx, self.y + dy)

    def scaled(self, factor: float) -> Point:
        return Point(self.x * factor, self.y * factor)

    def toward(self, other: Point, fraction: float) -> Point:
        """The point ``fraction`` of the way from here to ``other``."""
        return Point(self.x + (other.x - self.x) * fraction, self.y + (other.y - self.y) * fraction)

    def truncated(self) -> Point:
        return Point(int(self.x), int(self.y))

    def distance_to(self, other: Point) -> float:
        return ((other.x - self.x) ** 2 + (other.y - self.y) ** 2) ** 0.5
