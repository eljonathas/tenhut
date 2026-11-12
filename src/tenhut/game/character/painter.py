from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager

import pygame
from pygame.typing import ColorLike, RectLike
from pygame.typing import Point as PygamePoint

from ..painting import Canvas, Palette
from .anatomy import Anatomy
from .limb import Limb


class Painter(Canvas):
    """A canvas in sprite coordinates: adds the outline margin, the breathing bob and a sideways shift."""

    def __init__(self, surface: pygame.Surface, bob: int = 0, shift: int = 0) -> None:
        super().__init__(surface)
        self._bob = bob
        self._shift = shift

    def grounded(self) -> Painter:
        """The same painter without the bob, for what stays on the floor."""
        return Painter(self.surface, bob=0, shift=self._shift)

    @contextmanager
    def shifted(self, dx: int) -> Iterator[None]:
        self._shift += dx
        try:
            yield
        finally:
            self._shift -= dx

    @contextmanager
    def clipped(self, area: RectLike) -> Iterator[None]:
        """Restricts drawing to ``area``, given in raw surface coordinates (no margin, no bob)."""
        self.surface.set_clip(pygame.Rect(area))
        try:
            yield
        finally:
            self.surface.set_clip(None)

    def rect(self, color: ColorLike, area: RectLike, *, border: int = 0) -> None:
        super().rect(color, self._placed(area), border=border)

    def ellipse(self, color: ColorLike, area: RectLike, *, border: int = 0) -> None:
        super().ellipse(color, self._placed(area), border=border)

    def line(self, color: ColorLike, start: PygamePoint, end: PygamePoint, *, width: int = 1) -> None:
        super().line(color, self._moved(start), self._moved(end), width=width)

    def polygon(self, color: ColorLike, points: Sequence[PygamePoint], *, border: int = 0) -> None:
        super().polygon(color, [self._moved(point) for point in points], border=border)

    def pixel(self, color: ColorLike, point: PygamePoint) -> None:
        super().pixel(color, self._moved(point))

    def outlined_rect(self, color: ColorLike, area: RectLike) -> None:
        """A rectangle with a one pixel dark rim, to separate arms from the torso."""
        rim = pygame.Rect(area).inflate(2, 2)
        self.rect(Palette.OUTLINE, rim)
        self.rect(color, area)

    def limb(self, color: ColorLike, limb: Limb) -> None:
        """A thick rounded limb with a dark rim."""
        rim = limb.thickness + 2
        self.line(Palette.OUTLINE, limb.start, limb.end, width=rim)
        for joint in (limb.start, limb.end):
            self.ellipse(Palette.OUTLINE, pygame.Rect(joint[0] - rim // 2, joint[1] - rim // 2, rim, rim))
        self.line(color, limb.start, limb.end, width=limb.thickness)
        for joint in (limb.start, limb.end):
            self.ellipse(
                color,
                pygame.Rect(
                    joint[0] - limb.thickness // 2, joint[1] - limb.thickness // 2, limb.thickness, limb.thickness
                ),
            )

    def _placed(self, area: RectLike) -> pygame.Rect:
        return pygame.Rect(area).move(self._shift + Anatomy.OUTLINE_MARGIN, self._bob + Anatomy.OUTLINE_MARGIN)

    def _moved(self, point: PygamePoint) -> tuple[float, float]:
        return point[0] + self._shift + Anatomy.OUTLINE_MARGIN, point[1] + self._bob + Anatomy.OUTLINE_MARGIN
