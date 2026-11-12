from __future__ import annotations

import random
from typing import ClassVar

import pygame

from ..painting import Canvas, Rgb


class MapBoard:
    """An operations map on the wall: green islands, a river and a red route through pinned towns."""

    FRAME: ClassVar[Rgb] = Rgb(112, 76, 44)
    CORK: ClassVar[Rgb] = Rgb(196, 160, 112)
    PAPER: ClassVar[Rgb] = Rgb(226, 216, 180)
    LAND: ClassVar[Rgb] = Rgb(150, 190, 130)
    RIVER: ClassVar[Rgb] = Rgb(90, 130, 200)
    ROUTE: ClassVar[Rgb] = Rgb(200, 40, 40)
    PIN: ClassVar[Rgb] = Rgb(220, 40, 40)
    SEED: ClassVar[int] = 3
    ISLANDS: ClassVar[int] = 4
    PINS: ClassVar[int] = 4

    def __init__(self, area: pygame.Rect) -> None:
        self._area = area

    def draw(self, canvas: Canvas) -> None:
        area = self._area
        rng = random.Random(self.SEED)
        canvas.rect(self.FRAME, area.inflate(4, 4))
        canvas.rect(self.CORK, area)
        canvas.rect(self.PAPER, (area.x + 3, area.y + 3, area.width - 6, area.height - 6))
        for _ in range(self.ISLANDS):
            x = area.x + rng.randrange(3, max(4, area.width - 16))
            y = area.y + rng.randrange(3, max(4, area.height - 10))
            canvas.ellipse(self.LAND, (x, y, 12, 7))
        canvas.line(self.RIVER, (area.x + 4, area.y + area.height - 6), (area.x + area.width - 6, area.y + 5))
        self._draw_route(canvas, rng)

    def _draw_route(self, canvas: Canvas, rng: random.Random) -> None:
        area = self._area
        pins = [
            (area.x + rng.randrange(5, area.width - 4), area.y + rng.randrange(4, area.height - 3))
            for _ in range(self.PINS)
        ]
        canvas.lines(self.ROUTE, pins)
        for x, y in pins:
            canvas.rect(self.PIN, (x - 1, y - 1, 2, 2))
