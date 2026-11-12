from __future__ import annotations

import random
from typing import ClassVar

from ..painting import Canvas, Rgb
from .perspective_grid import PerspectiveGrid


class CraterField:
    """Shell craters scattered over the ground at fixed pseudo-random spots."""

    SEED: ClassVar[int] = 11
    COUNT: ClassVar[int] = 7
    NEAREST_DEPTH: ClassVar[float] = 1.2
    FARTHEST_DEPTH: ClassVar[float] = 6
    LATERAL_SPREAD: ClassVar[float] = 0.6
    WIDTH: ClassVar[int] = 26
    HEIGHT: ClassVar[int] = 7
    SHADOW: ClassVar[float] = 0.7
    RIM: ClassVar[float] = 1.15

    def __init__(self, grid: PerspectiveGrid, mud: Rgb, world_width: int) -> None:
        self._grid = grid
        self._mud = mud
        self._world_width = world_width

    def draw(self, canvas: Canvas) -> None:
        rng = random.Random(self.SEED)
        reach = self._world_width * self.LATERAL_SPREAD
        for _ in range(self.COUNT):
            depth = rng.uniform(self.NEAREST_DEPTH, self.FARTHEST_DEPTH)
            self._draw_crater(canvas, depth, rng.uniform(-reach, reach))

    def _draw_crater(self, canvas: Canvas, depth: float, lateral: float) -> None:
        spot = self._grid.project(depth, lateral)
        width, height = max(4, int(self.WIDTH / depth)), max(2, int(self.HEIGHT / depth))
        left, top = spot.x - width // 2, spot.y - height // 2
        canvas.ellipse(self._mud.shaded(self.SHADOW), (left, top, width, height))
        canvas.ellipse(self._mud.shaded(self.RIM), (left, top - 1, width, max(1, height // 2)), border=1)
