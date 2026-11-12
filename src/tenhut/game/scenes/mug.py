from __future__ import annotations

from typing import ClassVar

from ..geometry import Point
from ..painting import Canvas, Palette, Rgb


class Mug:
    """A steaming mug resting on the desk; the steam wisps cycle with time."""

    RED: ClassVar[Rgb] = Rgb(226, 70, 60)
    TIN: ClassVar[Rgb] = Rgb(150, 156, 164)
    STEAM: ClassVar[Rgb] = Rgb(236, 236, 242)
    STEAM_WISPS: ClassVar[int] = 3
    STEAM_RATE: ClassVar[float] = 4

    def __init__(self, position: Point, color: Rgb = RED) -> None:
        self._position = position
        self._color = color

    def draw(self, canvas: Canvas, elapsed: float, offset: Point) -> None:
        x, y = self._position.x + offset.x, self._position.y + offset.y
        self._draw_body(canvas, x, y)
        self._draw_steam(canvas, Point(x, y), elapsed)

    def _draw_body(self, canvas: Canvas, x: float, y: float) -> None:
        color, white = self._color, Palette.WHITE
        canvas.rect(Palette.OUTLINE, (x - 1, y - 1, 10, 11))
        canvas.rect(Palette.OUTLINE, (x + 8, y + 1, 4, 6))
        canvas.rect(color, (x, y, 8, 9))
        canvas.rect(white, (x, y, 8, 1))
        canvas.rect(Palette.BROWN_DARK, (x + 1, y + 1, 6, 1))
        canvas.rect(color, (x + 8, y + 2, 2, 4))
        canvas.rect(white, (x + 2, y + 4, 4, 2))

    def _draw_steam(self, canvas: Canvas, origin: Point, elapsed: float) -> None:
        x, y = origin
        phase = int(elapsed * self.STEAM_RATE) % self.STEAM_WISPS
        for wisp in range(self.STEAM_WISPS):
            wisp_x, wisp_y = x + 2 + ((wisp + phase) % 2) * 2, y - 2 - wisp * 2
            if wisp_y >= 0:
                canvas.pixel(self.STEAM, (wisp_x, wisp_y))
