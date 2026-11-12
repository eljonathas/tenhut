from __future__ import annotations

from typing import ClassVar

from ..geometry import Point
from ..painting import Canvas, Rgb
from .depth_point import DepthPoint
from .side import Side
from .viewport import Viewport


class PerspectiveGrid:
    """One-point perspective: everything converges on (vanishing_x, horizon_y).

    Depth 1 is the nearest line (the bottom of the canvas); larger depths shrink toward the horizon.
    """

    GROUND_BAND_COUNT: ClassVar[int] = 9
    BAND_GROWTH: ClassVar[float] = 0.45
    CORRIDOR_MIN_HALF_WIDTH: ClassVar[int] = 60
    CORRIDOR_SPAN_FACTOR: ClassVar[float] = 1.25
    DEPTH_STEP: ClassVar[float] = 0.9

    def __init__(self, viewport: Viewport, horizon_drop: int = 0) -> None:
        """``horizon_drop`` lowers the ground's far edge a few pixels so it tucks under the hills."""
        self._viewport = viewport
        self._horizon_y = viewport.horizon_y + horizon_drop

    @property
    def vanishing_x(self) -> int:
        return self._viewport.vanishing_x

    @property
    def width(self) -> int:
        return self._viewport.width

    @property
    def horizon_y(self) -> int:
        return self._horizon_y

    @property
    def ground_height(self) -> int:
        return self._viewport.height - self._horizon_y

    @property
    def half_width(self) -> float:
        """Half the width of the street or corridor at depth 1."""
        return max(self.CORRIDOR_MIN_HALF_WIDTH, self._viewport.span * self.CORRIDOR_SPAN_FACTOR)

    def project(self, depth: float, lateral: float) -> Point:
        """Where a ground spot ``lateral`` pixels off the vanishing line (at depth 1) lands at ``depth``."""
        return Point(self.vanishing_x + lateral / depth, self._horizon_y + self.ground_height / depth)

    def point_at(self, depth: float, side: Side) -> Point:
        """The foot of the building facade on ``side`` of the street at ``depth``."""
        return Point(self.vanishing_x + side * self.half_width / depth, self._horizon_y + self.ground_height / depth)

    def depth_points(self, side: Side, spread: float, count: int) -> list[DepthPoint]:
        """``count`` evenly spaced posts along a line leaving the vanishing point, far to near."""
        posts = []
        for index in range(1, count + 1):
            depth = 1 + (count - index) * self.DEPTH_STEP
            posts.append(
                DepthPoint(
                    self.vanishing_x + side * spread / depth, self._horizon_y + self.ground_height / depth, 1 / depth
                )
            )
        return posts

    def floor_ray_end(self, back_x: int, back_wall_bottom: int) -> Point:
        """Where the floor line through a point on the back wall's base reaches the bottom edge."""
        stretch = (self._viewport.height - self._horizon_y) / max(1, back_wall_bottom - self._horizon_y)
        return Point(self.vanishing_x + (back_x - self.vanishing_x) * stretch, self._viewport.height)

    def paint_ground(self, canvas: Canvas, base: Rgb, stripe: Rgb) -> None:
        """Flat ground colour with stripes that widen toward the viewer."""
        width = self._viewport.width
        canvas.rect(base, (0, self._horizon_y, width, self.ground_height))
        for index in range(1, self.GROUND_BAND_COUNT + 1, 2):
            top = self._band_edge(index)
            bottom = self._band_edge(index + 0.5)
            canvas.rect(stripe, (0, top, width, max(1, bottom - top)))

    def _band_edge(self, index: float) -> int:
        return self._horizon_y + int(self.ground_height * (1 - 1 / (1 + index * self.BAND_GROWTH)))
