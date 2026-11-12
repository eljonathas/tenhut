from __future__ import annotations

import random
from typing import ClassVar

from ..painting import Canvas, Palette, Rgb
from .viewport import Viewport


class Desk:
    """The wooden top in the foreground, with grain scratches drawn from a fixed seed."""

    SEED: ClassVar[int] = 4
    SCRATCH_SPACING: ClassVar[int] = 14
    SCRATCH_MIN_LENGTH: ClassVar[int] = 8
    SCRATCH_MAX_LENGTH: ClassVar[int] = 24
    GRAIN_INSET: ClassVar[int] = 3

    def __init__(self, top: Rgb, grain: Rgb, highlight: Rgb) -> None:
        self._top = top
        self._grain = grain
        self._highlight = highlight

    def draw(self, canvas: Canvas, viewport: Viewport) -> None:
        desk_y, width, height = viewport.desk_y, viewport.width, viewport.height
        canvas.rect(Palette.OUTLINE, (0, desk_y - 1, width, height - desk_y + 1))
        canvas.rect(self._top, (0, desk_y, width, height - desk_y))
        canvas.rect(self._highlight, (0, desk_y, width, 1))
        rng = random.Random(self.SEED)
        for _ in range(width // self.SCRATCH_SPACING):
            y = rng.randrange(desk_y + self.GRAIN_INSET, height)
            x = rng.randrange(width)
            canvas.line(self._grain, (x, y), (x + rng.randint(self.SCRATCH_MIN_LENGTH, self.SCRATCH_MAX_LENGTH), y))
