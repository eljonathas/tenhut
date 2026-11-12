from __future__ import annotations

import itertools
from typing import ClassVar

import pygame

from ..painting import Canvas, Palette, Rgb


class MapSheet:
    """A big paper map spread on the field table, in perspective, with fold lines and a marked route."""

    PAPER: ClassVar[Rgb] = Rgb(226, 212, 168)
    FOLD: ClassVar[Rgb] = Rgb(196, 180, 136)
    ROUTE: ClassVar[Rgb] = Rgb(200, 40, 40)
    FOLDS: ClassVar[int] = 4
    FLARE: ClassVar[int] = 7
    FOLD_FLARE_DIVISOR: ClassVar[int] = 6
    TARGET_ARM: ClassVar[int] = 2

    def __init__(self, area: pygame.Rect, vanishing_x: int) -> None:
        self._area = area
        self._vanishing_x = vanishing_x

    def draw(self, canvas: Canvas) -> None:
        area = self._area
        left, right, bottom = area.left, area.right, area.bottom
        canvas.polygon(
            Palette.OUTLINE, [(left - 1, area.y + 3), (right + 1, area.y + 3), (right + 8, bottom), (left - 8, bottom)]
        )
        canvas.polygon(
            self.PAPER,
            [(left, area.y + 4), (right, area.y + 4), (right + self.FLARE, bottom), (left - self.FLARE, bottom)],
        )
        for fold in range(1, self.FOLDS):
            x = left + area.width * fold // self.FOLDS
            canvas.line(self.FOLD, (x, area.y + 4), (x + (x - self._vanishing_x) // self.FOLD_FLARE_DIVISOR, bottom))
        self._draw_route(canvas)

    def _draw_route(self, canvas: Canvas) -> None:
        area = self._area
        middle = area.y + area.height // 2
        route = [
            (area.x + 8, area.bottom - 3),
            (area.x + area.width // 3, middle),
            (area.x + area.width // 2, middle + 3),
            (area.x + area.width - 10, area.y + 8),
        ]
        for start, end in itertools.pairwise(route):
            canvas.line(self.ROUTE, start, end)
        x, y = route[-1]
        arm = self.TARGET_ARM
        canvas.line(self.ROUTE, (x - arm, y - arm), (x + arm, y + arm))
        canvas.line(self.ROUTE, (x - arm, y + arm), (x + arm, y - arm))
