from __future__ import annotations

from typing import ClassVar

from ..painting import Canvas, Palette, Rgb


class Tent:
    """A canvas tent pitched on the horizon."""

    CANVAS: ClassVar[Rgb] = Rgb(110, 128, 70)
    SHADOW: ClassVar[Rgb] = Rgb(78, 92, 50)
    HALF_WIDTH: ClassVar[int] = 11
    PEAK_HEIGHT: ClassVar[int] = 12
    GROUND_DROP: ClassVar[int] = 3

    def __init__(self, center_x: int, horizon_y: int) -> None:
        self._center_x = center_x
        self._horizon_y = horizon_y

    def draw(self, canvas: Canvas) -> None:
        x, y = self._center_x, self._horizon_y
        left = (x - self.HALF_WIDTH, y + self.GROUND_DROP)
        right = (x + self.HALF_WIDTH, y + self.GROUND_DROP)
        peak = (x, y - self.PEAK_HEIGHT)
        canvas.polygon(self.CANVAS, [left, peak, right])
        canvas.polygon(self.SHADOW, [peak, right, (x + 3, y + self.GROUND_DROP)])
        canvas.lines(Palette.OUTLINE, [left, peak, right])
