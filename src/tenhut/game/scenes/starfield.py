from __future__ import annotations

from typing import ClassVar, NamedTuple

import pygame

from ..painting import Canvas, Rgb
from ..random_source import RandomSource


class _Star(NamedTuple):
    across: float
    down: float


class Starfield:
    """Star positions as fractions of whatever area they are painted on."""

    COUNT: ClassVar[int] = 60
    COLOR: ClassVar[Rgb] = Rgb(230, 230, 255)

    def __init__(self, randomness: RandomSource) -> None:
        self._stars = [_Star(randomness.random(), randomness.random()) for _ in range(self.COUNT)]

    def paint(self, canvas: Canvas, area: pygame.Rect, depth: float, *, limit: int | None = None) -> None:
        """Dots over ``area``; ``depth`` is the fraction of its height the stars may reach."""
        for star in self._stars[:limit]:
            canvas.pixel(
                self.COLOR, (area.x + int(star.across * area.width), area.y + int(star.down * area.height * depth))
            )
