from __future__ import annotations

from typing import ClassVar

from ..painting import Canvas, Rgb
from .perspective_grid import PerspectiveGrid
from .side import Side


class ParadeStreet:
    """The avenue itself: pavement, tarmac, kerbs, the dashed centre line and the far skyline."""

    PAVEMENT: ClassVar[Rgb] = Rgb(170, 164, 150)
    ROAD: ClassVar[Rgb] = Rgb(92, 92, 100)
    KERB: ClassVar[Rgb] = Rgb(200, 196, 184)
    CENTRE_LINE: ClassVar[Rgb] = Rgb(240, 230, 160)
    CENTRE_DASH_DEPTHS: ClassVar[tuple[float, ...]] = (1.3, 1.8, 2.6, 3.8, 5.6)
    DASH_LENGTH: ClassVar[float] = 0.25
    PAVEMENT_BLEED: ClassVar[int] = 40
    ROAD_NARROWING: ClassVar[float] = 0.25
    KERB_REACH: ClassVar[float] = 0.75
    SKYLINE_DEPTH: ClassVar[int] = 9
    SKYLINE_HEIGHT_SHARE: ClassVar[float] = 0.6
    SKYLINE_OVERLAP: ClassVar[int] = 4
    SKYLINE_SHADE: ClassVar[float] = 0.75

    def __init__(self, grid: PerspectiveGrid) -> None:
        self._grid = grid

    def paint(self, canvas: Canvas) -> None:
        grid = self._grid
        x, horizon_y = grid.vanishing_x, grid.horizon_y
        height = horizon_y + grid.ground_height
        left, right = grid.point_at(1, Side.LEFT).x, grid.point_at(1, Side.RIGHT).x
        canvas.rect(self.PAVEMENT, (0, horizon_y, canvas.surface.get_width(), grid.ground_height))
        canvas.polygon(
            self.PAVEMENT,
            [
                (x - 1, horizon_y),
                (x + 1, horizon_y),
                (right + self.PAVEMENT_BLEED, height),
                (left - self.PAVEMENT_BLEED, height),
            ],
        )
        road = [
            (x, horizon_y),
            (x, horizon_y),
            (right - (right - x) * self.ROAD_NARROWING, height),
            (left + (x - left) * self.ROAD_NARROWING, height),
        ]
        canvas.polygon(self.ROAD, road)
        for side in Side:
            canvas.line(self.KERB, (x, horizon_y), (x + side * (right - x) * self.KERB_REACH, height), width=2)
        self._paint_centre_line(canvas)

    def _paint_centre_line(self, canvas: Canvas) -> None:
        for depth in self.CENTRE_DASH_DEPTHS:
            start, end = self._grid.project(depth, 0), self._grid.project(depth + self.DASH_LENGTH, 0)
            canvas.line(
                self.CENTRE_LINE,
                (self._grid.vanishing_x, start.y),
                (self._grid.vanishing_x, end.y),
                width=max(1, int(3 / depth)),
            )

    def paint_skyline(self, canvas: Canvas, horizon_color: Rgb) -> None:
        """The row of far-away buildings at the end of the avenue, drawn behind the general."""
        left, right = (
            self._grid.point_at(self.SKYLINE_DEPTH, Side.LEFT).x,
            self._grid.point_at(self.SKYLINE_DEPTH, Side.RIGHT).x,
        )
        tallness = int(self._grid.horizon_y * self.SKYLINE_HEIGHT_SHARE / self.SKYLINE_DEPTH)
        top = self._grid.horizon_y - tallness - self.SKYLINE_OVERLAP
        canvas.rect(
            horizon_color.shaded(self.SKYLINE_SHADE), (left, top, right - left, tallness + self.SKYLINE_OVERLAP)
        )
