from __future__ import annotations

import random
from typing import ClassVar

import pygame

from ..painting import Canvas, Palette, Rgb
from .viewport import Viewport


class SandbagWall:
    """The parapet of staggered sandbags that fills the foreground; each row is jittered from a fixed seed."""

    SAND: ClassVar[Rgb] = Rgb(198, 172, 116)
    SHADOW: ClassVar[Rgb] = Rgb(158, 130, 82)
    HIGHLIGHT: ClassVar[Rgb] = Rgb(220, 198, 144)
    SEED: ClassVar[int] = 5
    MIN_BAG_HEIGHT: ClassVar[int] = 7
    BAG_ASPECT: ClassVar[float] = 1.9
    TOP_OVERLAP: ClassVar[int] = 2
    ROWS_PER_DESK: ClassVar[int] = 3

    def draw(self, canvas: Canvas, viewport: Viewport) -> None:
        bag_height = max(self.MIN_BAG_HEIGHT, viewport.desk_height // self.ROWS_PER_DESK)
        bag_width = int(bag_height * self.BAG_ASPECT)
        rng = random.Random(self.SEED)
        rows = range(viewport.desk_y - self.TOP_OVERLAP, viewport.height + bag_height, bag_height - 1)
        for row, top in enumerate(rows):
            stagger = 0 if row % 2 == 0 else bag_width // 2
            for left in range(-bag_width + stagger, viewport.width + bag_width, bag_width - 2):
                jitter = rng.randint(-1, 1) if row else 0
                self._draw_bag(canvas, pygame.Rect(left, top + jitter, bag_width, bag_height))

    def _draw_bag(self, canvas: Canvas, bag: pygame.Rect) -> None:
        left, top, width, height = bag
        canvas.ellipse(Palette.OUTLINE, (left - 1, top - 1, width + 2, height + 2))
        canvas.ellipse(self.SAND, (left, top, width, height))
        canvas.line(self.HIGHLIGHT, (left + 3, top + 1), (left + width - 5, top + 1))
        canvas.line(self.SHADOW, (left + 3, top + height - 2), (left + width - 4, top + height - 2))
        canvas.pixel(self.SHADOW, (left + width // 2, top + height // 2))
