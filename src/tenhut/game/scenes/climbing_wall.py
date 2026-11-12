from __future__ import annotations

from typing import ClassVar

from ..painting import Canvas, Palette, Rgb


class ClimbingWall:
    """A small wooden obstacle wall on the horizon."""

    PLANKS: ClassVar[Rgb] = Rgb(150, 110, 70)
    SLATS: ClassVar[Rgb] = Rgb(120, 84, 50)
    WIDTH: ClassVar[int] = 12

    def __init__(self, left: int, horizon_y: int) -> None:
        self._left = left
        self._horizon_y = horizon_y

    def draw(self, canvas: Canvas) -> None:
        x, y = self._left, self._horizon_y
        canvas.rect(Palette.OUTLINE, (x - 1, y - 13, self.WIDTH + 2, 16))
        canvas.rect(self.PLANKS, (x, y - 12, self.WIDTH, 14))
        for slat_y in range(y - 10, y + 2, 3):
            canvas.line(self.SLATS, (x, slat_y), (x + self.WIDTH - 1, slat_y))
