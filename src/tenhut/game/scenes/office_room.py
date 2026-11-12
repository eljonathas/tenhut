from __future__ import annotations

from typing import ClassVar

import pygame

from ..painting import Canvas, Rgb
from .perspective_grid import PerspectiveGrid
from .viewport import Viewport


class OfficeRoom:
    """The headquarters room: a back wall, two side walls, a ceiling and a plank floor in one-point perspective."""

    WALL: ClassVar[Rgb] = Rgb(196, 182, 142)
    SIDE_WALL: ClassVar[Rgb] = Rgb(166, 152, 114)
    CEILING: ClassVar[Rgb] = Rgb(150, 140, 108)
    FLOOR: ClassVar[Rgb] = Rgb(128, 88, 54)
    PLANK: ClassVar[Rgb] = Rgb(104, 70, 42)
    BASEBOARD: ClassVar[Rgb] = Rgb(92, 64, 40)
    WAINSCOT: ClassVar[Rgb] = Rgb(150, 120, 84)
    EDGE_SHADE: ClassVar[float] = 0.8
    MIN_HALF_WIDTH: ClassVar[int] = 56
    HALF_WIDTH_SHARE: ClassVar[float] = 0.24
    SIDE_MARGIN: ClassVar[int] = 6
    CEILING_MARGIN: ClassVar[int] = 3
    HEIGHT_ABOVE_HORIZON: ClassVar[float] = 0.36
    HEIGHT_BELOW_HORIZON: ClassVar[float] = 0.14
    DESK_CLEARANCE: ClassVar[int] = 4
    PLANK_SPACING: ClassVar[int] = 9
    CROSS_BOARDS: ClassVar[int] = 4
    CROSS_BOARD_GROWTH: ClassVar[float] = 0.6
    WAINSCOT_HEIGHT_SHARE: ClassVar[float] = 0.68

    def __init__(self, viewport: Viewport) -> None:
        self._viewport = viewport
        half_width = max(self.MIN_HALF_WIDTH, int(viewport.width * self.HALF_WIDTH_SHARE))
        left = max(self.SIDE_MARGIN, viewport.vanishing_x - half_width)
        right = min(viewport.width - self.SIDE_MARGIN, viewport.vanishing_x + half_width)
        top = max(self.CEILING_MARGIN, viewport.horizon_y - int(viewport.height * self.HEIGHT_ABOVE_HORIZON))
        bottom = min(
            viewport.desk_y - self.DESK_CLEARANCE, viewport.horizon_y + int(viewport.height * self.HEIGHT_BELOW_HORIZON)
        )
        self._back_wall = pygame.Rect(left, top, right - left, bottom - top)

    @property
    def back_wall(self) -> pygame.Rect:
        return self._back_wall

    def height_share(self, share: float) -> int:
        """A vertical distance down the back wall, as a share of its height."""
        return int(self._back_wall.height * share)

    def paint(self, canvas: Canvas) -> None:
        self._paint_walls(canvas)
        self._paint_floor(canvas)
        self._paint_edges(canvas)
        wall = self._back_wall
        canvas.rect(self.WAINSCOT, (wall.x, wall.y + self.height_share(self.WAINSCOT_HEIGHT_SHARE), wall.width, 2))

    def _paint_walls(self, canvas: Canvas) -> None:
        width, height = self._viewport.size
        wall = self._back_wall
        canvas.surface.fill(self.WALL)
        canvas.polygon(self.CEILING, [(0, 0), (width, 0), (wall.right, wall.top), (wall.left, wall.top)])
        canvas.polygon(self.SIDE_WALL, [(0, 0), (wall.left, wall.top), (wall.left, wall.bottom), (0, height)])
        canvas.polygon(self.SIDE_WALL, [(width, 0), (wall.right, wall.top), (wall.right, wall.bottom), (width, height)])
        canvas.rect(self.WALL, wall)

    def _paint_floor(self, canvas: Canvas) -> None:
        width, height = self._viewport.size
        wall = self._back_wall
        grid = PerspectiveGrid(self._viewport)
        canvas.polygon(self.FLOOR, [(0, height), (wall.left, wall.bottom), (wall.right, wall.bottom), (width, height)])
        for plank_x in range(wall.left, wall.right + 1, self.PLANK_SPACING):
            canvas.line(self.PLANK, (plank_x, wall.bottom), grid.floor_ray_end(plank_x, wall.bottom))
        for board in range(1, self.CROSS_BOARDS + 1):
            y = wall.bottom + int((height - wall.bottom) * (1 - 1 / (1 + board * self.CROSS_BOARD_GROWTH)))
            canvas.line(self.PLANK, (0, y), (width, y))
        canvas.rect(self.BASEBOARD, (wall.left, wall.bottom - 2, wall.width, 2))

    def _paint_edges(self, canvas: Canvas) -> None:
        width, height = self._viewport.size
        wall = self._back_wall
        edge = self.SIDE_WALL.shaded(self.EDGE_SHADE)
        corners = (
            ((0, 0), wall.topleft),
            ((width, 0), wall.topright),
            ((0, height), wall.bottomleft),
            ((width, height), wall.bottomright),
        )
        for outer, inner in corners:
            canvas.line(edge, outer, inner)
        canvas.rect(edge, wall, border=1)
