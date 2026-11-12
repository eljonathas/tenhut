from __future__ import annotations

import math
from typing import ClassVar

from ..geometry import Point
from ..painting import Canvas, Rgb


class Bunting:
    """A string of little flags hung across the street from facade to facade."""

    STRING: ClassVar[Rgb] = Rgb(60, 50, 50)
    FLAG_COLORS: ClassVar[tuple[Rgb, ...]] = (Rgb(220, 60, 60), Rgb(250, 214, 90), Rgb(70, 150, 90), Rgb(90, 140, 220))
    SEGMENTS: ClassVar[int] = 16
    SAG: ClassVar[int] = 10
    FLAG_SIZE: ClassVar[int] = 6

    def __init__(self, depth: float, left_end: Point, right_end: Point) -> None:
        """The string is fixed at both ends, which sit at the same height."""
        self._depth = depth
        self._left_end = left_end
        self._right_end = right_end

    def draw(self, canvas: Canvas) -> None:
        points = [self._point_at(step / self.SEGMENTS) for step in range(self.SEGMENTS + 1)]
        canvas.lines(self.STRING, points)
        size = max(2, int(self.FLAG_SIZE / self._depth))
        for index, (x, y) in enumerate(points[1:-1]):
            color = self.FLAG_COLORS[index % len(self.FLAG_COLORS)]
            canvas.polygon(color, [(x - size // 2, y), (x + size // 2, y), (x, y + size)])

    def _point_at(self, along: float) -> tuple[float, float]:
        """A point on the sagging string; ``along`` runs from 0 (left wall) to 1 (right wall)."""
        sag = math.sin(along * math.pi) * self.SAG / self._depth
        return self._left_end.x + (self._right_end.x - self._left_end.x) * along, self._left_end.y + sag
