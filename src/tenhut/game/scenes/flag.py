from __future__ import annotations

import math
from typing import ClassVar, Final

import pygame

from ..geometry import Point
from ..painting import Canvas, Palette, Rgb

_STAR_PIXELS: Final = frozenset(
    Point(x, y)
    for x, y in (
        (2, 0),
        (2, 1),
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 2),
        (4, 2),
        (1, 3),
        (2, 3),
        (3, 3),
        (1, 4),
        (3, 4),
        (0, 5),
        (4, 5),
    )
)


class Flag:
    """A red banner with a gold star, rippling in the wind with its edge pinned to the pole.

    The wave grows toward the free end, its amplitude follows the cloth size and the folds are
    shaded, so even a tiny flag reads as cloth rather than as a sign.
    """

    CLOTH: ClassVar[Rgb] = Rgb(186, 48, 52)
    STAR: ClassVar[Rgb] = Rgb(250, 214, 90)
    AMPLITUDE_RATIO: ClassVar[float] = 0.17
    STIFFNESS_EXPONENT: ClassVar[float] = 0.8
    WAVE_SPEED: ClassVar[float] = 4.2
    WAVE_LAG: ClassVar[float] = 0.5
    FLUTTER_SHARE: ClassVar[float] = 0.25
    FLUTTER_SPEED: ClassVar[float] = 7.1
    FLUTTER_LAG: ClassVar[float] = 0.9
    FOLD_LIGHT: ClassVar[float] = 0.18
    TAIL_COLUMNS: ClassVar[int] = 5
    STAR_ORIGIN: ClassVar[Point] = Point(2, 3)

    def __init__(self, area: pygame.Rect) -> None:
        self._area = area

    def draw(self, canvas: Canvas, elapsed: float) -> None:
        surface_width = canvas.surface.get_width()
        for column in range(self._area.width):
            if 0 <= self._area.x + column < surface_width:
                self._draw_column(canvas, column, elapsed)

    def _draw_column(self, canvas: Canvas, column: int, elapsed: float) -> None:
        area = self._area
        stiffness = (column / max(1, area.width - 1)) ** self.STIFFNESS_EXPONENT
        phase = elapsed * self.WAVE_SPEED - column * self.WAVE_LAG
        flutter = self.FLUTTER_SHARE * math.sin(elapsed * self.FLUTTER_SPEED - column * self.FLUTTER_LAG)
        amplitude = max(1.0, area.height * self.AMPLITUDE_RATIO)
        sway = round(amplitude * stiffness * (math.sin(phase) + flutter))
        light = 1 + self.FOLD_LIGHT * math.cos(phase) * stiffness
        height = canvas.surface.get_height()
        for row in range(area.height):
            color = self._cloth_color(column, row)
            if color is not None and 0 <= area.y + row + sway < height:
                canvas.pixel(color.shaded(light), (area.x + column, area.y + row + sway))
        for edge_y in (area.y - 1 + sway, area.y + area.height + sway):
            if 0 <= edge_y < height:
                canvas.pixel(Palette.OUTLINE, (area.x + column, edge_y))

    def _cloth_color(self, column: int, row: int) -> Rgb | None:
        """The pixel's colour, or None where the swallow-tail notch cuts the cloth away."""
        width, height = self._area.width, self._area.height
        if column >= width - self.TAIL_COLUMNS and abs(row - height // 2) < column - (width - self.TAIL_COLUMNS - 1):
            return None
        star_cell = Point(column - width // 2 + self.STAR_ORIGIN.x, row - height // 2 + self.STAR_ORIGIN.y)
        if star_cell in _STAR_PIXELS:
            return self.STAR
        return Palette.GOLD if row in (1, height - 2) else self.CLOTH
