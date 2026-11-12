from __future__ import annotations

from typing import ClassVar

import pygame

from ..geometry import Point
from ..painting import Canvas, Palette, Rgb
from .star_shape import StarShape


class StreetBanner:
    """The big festive banner slung between two rooftops over the general's head, with three gold stars."""

    ROPE: ClassVar[Rgb] = Rgb(60, 50, 50)
    CLOTH: ClassVar[Rgb] = Rgb(186, 48, 52)
    HEM: ClassVar[Rgb] = Rgb(150, 34, 40)
    STAR: ClassVar[Rgb] = Rgb(250, 214, 90)
    WIDTH_SHARE: ClassVar[float] = 0.5
    HEIGHT_SHARE: ClassVar[float] = 0.13
    MIN_HEIGHT: ClassVar[int] = 8
    ANCHOR_DROP: ClassVar[int] = 2
    STARS: ClassVar[int] = 3
    STAR_INNER_RATIO: ClassVar[float] = 0.45
    FRINGE_STEP: ClassVar[int] = 4

    def __init__(self, roofs: tuple[Point, Point], vanishing_x: int, horizon_y: int) -> None:
        left, right = roofs[0].moved(dy=self.ANCHOR_DROP), roofs[1].moved(dy=self.ANCHOR_DROP)
        cloth_width = int((right.x - left.x) * self.WIDTH_SHARE)
        cloth_height = max(self.MIN_HEIGHT, int(horizon_y * self.HEIGHT_SHARE))
        sag = max(2, cloth_height // 3)
        cloth_x = vanishing_x - cloth_width // 2
        cloth_top = int(min(left.y, right.y)) + sag
        self._ropes = (
            (left, Point(cloth_x, cloth_top + sag)),
            (Point(cloth_x + cloth_width, cloth_top + sag), right),
        )
        self._cloth = pygame.Rect(cloth_x, cloth_top + sag, cloth_width, cloth_height)

    def draw(self, canvas: Canvas) -> None:
        for start, end in self._ropes:
            middle = ((start.x + end.x) / 2, max(start.y, end.y) + 3)
            canvas.lines(self.ROPE, [start, middle, end])
        cloth = self._cloth
        canvas.rect(Palette.OUTLINE, cloth.inflate(2, 2))
        canvas.rect(self.CLOTH, cloth)
        canvas.rect(Palette.GOLD, cloth, border=1)
        canvas.line(self.HEM, (cloth.x + 1, cloth.bottom - 2), (cloth.right - 2, cloth.bottom - 2))
        self._draw_stars(canvas)
        for fringe_x in range(cloth.x, cloth.right, self.FRINGE_STEP):
            canvas.line(Palette.GOLD, (fringe_x, cloth.bottom), (fringe_x, cloth.bottom + 2))

    def _draw_stars(self, canvas: Canvas) -> None:
        cloth = self._cloth
        radius = max(2, self._cloth.height // 3)
        star = StarShape(radius, radius * self.STAR_INNER_RATIO)
        for index in range(self.STARS):
            center_x = cloth.x + cloth.width * (index + 1) // (self.STARS + 1)
            canvas.polygon(self.STAR, star.vertices(center_x, cloth.centery))
