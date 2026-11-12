from __future__ import annotations

import math
from typing import ClassVar

import pygame

from ..painting import Canvas, Palette, Rgb


class Banner:
    """A tall banner hanging from a rod: the foot swings more than the top in the breeze."""

    CLOTH: ClassVar[Rgb] = Rgb(186, 48, 52)
    CLOTH_STRIPE: ClassVar[Rgb] = Rgb(164, 38, 44)
    EMBLEM: ClassVar[Rgb] = Rgb(250, 214, 90)
    SWING: ClassVar[float] = 2.2
    SWING_SPEED: ClassVar[float] = 1.6
    SECOND_SWING: ClassVar[float] = 0.6
    SECOND_SPEED: ClassVar[float] = 3.1
    STRIPE_ROWS: ClassVar[int] = 3
    STRIPE_CYCLE: ClassVar[int] = 4
    EMBLEM_MIN_WIDTH: ClassVar[int] = 5
    EMBLEM_DRIFT: ClassVar[float] = 0.1

    def __init__(self, area: pygame.Rect, phase: float) -> None:
        self._area = area
        self._phase = phase

    def draw(self, canvas: Canvas, elapsed: float) -> None:
        self._draw_cloth(canvas, elapsed)
        self._draw_tip(canvas, elapsed)
        self._draw_emblem(canvas, elapsed)
        area = self._area
        canvas.line(Palette.OUTLINE, (area.x - 2, area.y - 1), (area.right + 1, area.y - 1))

    def _swing(self, elapsed: float) -> float:
        return math.sin(elapsed * self.SWING_SPEED + self._phase) * self.SWING

    def _draw_cloth(self, canvas: Canvas, elapsed: float) -> None:
        area = self._area
        surface_width, surface_height = canvas.surface.get_size()
        for row in range(area.height):
            hang = (row / max(1, area.height - 1)) ** 2
            second = math.sin(elapsed * self.SECOND_SPEED + self._phase * 2) * self.SECOND_SWING * hang
            sway = round(self._swing(elapsed) * hang + second)
            for column in range(-1, area.width + 1):
                x, y = area.x + column + sway, area.y + row
                if 0 <= x < surface_width and 0 <= y < surface_height:
                    canvas.pixel(self._pixel_color(column, row), (x, y))

    def _pixel_color(self, column: int, row: int) -> Rgb:
        width = self._area.width
        if column in (-1, width):
            return Palette.OUTLINE
        if column in (0, width - 1):
            return Palette.GOLD
        return self.CLOTH if (row // self.STRIPE_ROWS) % self.STRIPE_CYCLE else self.CLOTH_STRIPE

    def _draw_tip(self, canvas: Canvas, elapsed: float) -> None:
        area = self._area
        end = round(self._swing(elapsed))
        point_depth = max(2, area.width // 2)
        tip = [
            (area.x - 1 + end, area.y + area.height),
            (area.x + area.width + end, area.y + area.height),
            (area.x + area.width // 2 + end, area.y + area.height + point_depth),
        ]
        canvas.polygon(Palette.OUTLINE, tip)

    def _draw_emblem(self, canvas: Canvas, elapsed: float) -> None:
        area = self._area
        if area.width < self.EMBLEM_MIN_WIDTH:
            return
        drift = round(self._swing(elapsed) * self.EMBLEM_DRIFT)
        center = (area.x + area.width // 2 + drift, area.y + area.height // 4)
        canvas.circle(self.EMBLEM, center, max(1, area.width // 4))
