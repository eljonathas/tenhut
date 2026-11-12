from __future__ import annotations

from typing import ClassVar

from ..painting import Canvas, Palette, Rgb
from .depth_point import DepthPoint


class Tire:
    """A training tire lying flat on the grass, seen as an ellipse that shrinks with distance."""

    RUBBER: ClassVar[Rgb] = Rgb(60, 60, 64)
    WIDTH: ClassVar[int] = 14
    HEIGHT: ClassVar[int] = 6

    def __init__(self, spot: DepthPoint, hole: Rgb) -> None:
        self._spot = spot
        self._hole = hole

    def draw(self, canvas: Canvas) -> None:
        x, y, scale = self._spot.x, self._spot.y, self._spot.scale
        width, height = max(3, int(self.WIDTH * scale)), max(2, int(self.HEIGHT * scale))
        canvas.ellipse(Palette.OUTLINE, (x - width // 2 - 1, y - height, width + 2, height + 2))
        canvas.ellipse(self.RUBBER, (x - width // 2, y - height + 1, width, height))
        hole = (x - width // 4, y - height + 1 + height // 4, max(1, width // 2), max(1, height // 2))
        canvas.ellipse(self._hole, hole)
