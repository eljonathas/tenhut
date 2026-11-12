from __future__ import annotations

import random
from dataclasses import dataclass
from typing import ClassVar

from ..geometry import Point
from ..painting import Canvas, Palette, Rgb
from .perspective_grid import PerspectiveGrid
from .side import Side


@dataclass(frozen=True, slots=True)
class Facade:
    """The street-side wall of one building between two depths; ``height`` is its roof height at depth 1."""

    grid: PerspectiveGrid
    side: Side
    far: float
    near: float
    height: float
    color: Rgb

    DOOR: ClassVar[Rgb] = Rgb(70, 46, 30)
    DARK_WINDOW: ClassVar[Rgb] = Rgb(60, 70, 90)
    LIT_WINDOW: ClassVar[Rgb] = Rgb(250, 220, 130)
    DARK_CHANCE: ClassVar[float] = 0.7
    CORNICE_SHADE: ClassVar[float] = 0.6
    WINDOW_COLUMNS: ClassVar[tuple[float, ...]] = (0.3, 0.65)
    WINDOW_FLOORS: ClassVar[tuple[float, ...]] = (0.18, 0.42, 0.66)

    def roof_y(self, depth: float) -> float:
        return self.grid.horizon_y - self.height / depth

    def covers(self, depth: float) -> bool:
        return self.near <= depth <= self.far

    def near_roof_corner(self) -> Point:
        return Point(self.grid.point_at(self.near, self.side).x, self.roof_y(self.near))

    def draw(self, canvas: Canvas, rng: random.Random) -> None:
        self._draw_wall(canvas)
        self._draw_door(canvas)
        for column in self.WINDOW_COLUMNS:
            for floor in self.WINDOW_FLOORS:
                color = self.DARK_WINDOW if rng.random() < self.DARK_CHANCE else self.LIT_WINDOW
                self._draw_window(canvas, Point(column, floor), color)

    def _draw_wall(self, canvas: Canvas) -> None:
        grid = self.grid
        far_foot, near_foot = grid.point_at(self.far, self.side), grid.point_at(self.near, self.side)
        far_roof, near_roof = self.roof_y(self.far), self.roof_y(self.near)
        wall = [(far_foot.x, far_roof), (near_foot.x, near_roof), (near_foot.x, near_foot.y), (far_foot.x, far_foot.y)]
        canvas.polygon(self.color, wall)
        canvas.polygon(Palette.OUTLINE, wall, border=1)
        canvas.line(self.color.shaded(self.CORNICE_SHADE), wall[0], wall[1], width=max(1, int(3 / self.near)))

    def _draw_door(self, canvas: Canvas) -> None:
        depth = (self.far + self.near) / 2
        foot = self.grid.point_at(depth, self.side)
        width, height = max(1, int(6 / depth)), max(2, int(11 / depth))
        canvas.rect(self.DOOR, (foot.x - width // 2, foot.y - height, width, height))

    def _draw_window(self, canvas: Canvas, cell: Point, color: Rgb) -> None:
        column, floor = cell
        depth = self.far + (self.near - self.far) * column
        foot = self.grid.point_at(depth, self.side)
        roof = self.roof_y(depth)
        top = roof + (foot.y - roof) * floor
        width, height = max(1, int(5 / depth)), max(1, int(6 / depth))
        canvas.rect(color, (foot.x - width // 2, top, width, height))
