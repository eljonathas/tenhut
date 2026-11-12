from __future__ import annotations

from collections.abc import Sequence

import pygame
from pygame.typing import ColorLike, RectLike
from pygame.typing import Point as PygamePoint


class Canvas:
    """Draws filled shapes on a surface; colour first, then geometry, as in a sentence."""

    def __init__(self, surface: pygame.Surface) -> None:
        self._surface = surface

    @property
    def surface(self) -> pygame.Surface:
        return self._surface

    def rect(self, color: ColorLike, area: RectLike, *, border: int = 0) -> None:
        pygame.draw.rect(self._surface, color, area, border)

    def ellipse(self, color: ColorLike, area: RectLike, *, border: int = 0) -> None:
        pygame.draw.ellipse(self._surface, color, area, border)

    def circle(self, color: ColorLike, center: PygamePoint, radius: float, *, border: int = 0) -> None:
        pygame.draw.circle(self._surface, color, center, radius, border)

    def line(self, color: ColorLike, start: PygamePoint, end: PygamePoint, *, width: int = 1) -> None:
        pygame.draw.line(self._surface, color, start, end, width)

    def lines(self, color: ColorLike, points: Sequence[PygamePoint], *, width: int = 1) -> None:
        pygame.draw.lines(self._surface, color, False, points, width)

    def polygon(self, color: ColorLike, points: Sequence[PygamePoint], *, border: int = 0) -> None:
        pygame.draw.polygon(self._surface, color, points, border)

    def pixel(self, color: ColorLike, point: PygamePoint) -> None:
        self._surface.set_at(point, color)
