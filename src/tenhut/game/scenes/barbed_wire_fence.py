from __future__ import annotations

from typing import ClassVar

from ..painting import Canvas, Rgb
from .depth_point import DepthPoint


class BarbedWireFence:
    """Crossed pickets joined by two strands of wire, running toward the horizon."""

    PICKET: ClassVar[Rgb] = Rgb(54, 44, 40)
    WIRE: ClassVar[Rgb] = Rgb(90, 90, 96)
    PICKET_HEIGHT: ClassVar[int] = 18
    PICKET_WIDTH: ClassVar[int] = 2
    STRANDS: ClassVar[tuple[float, float]] = (0.35, 0.75)

    def __init__(self, posts: list[DepthPoint]) -> None:
        self._posts = posts

    def draw(self, canvas: Canvas) -> None:
        previous: tuple[DepthPoint, int] | None = None
        for post in self._posts:
            height = max(3, int(self.PICKET_HEIGHT * post.scale))
            self._draw_picket(canvas, post, height)
            if previous is not None:
                self._draw_wire(canvas, previous, (post, height))
            previous = (post, height)

    def _draw_picket(self, canvas: Canvas, post: DepthPoint, height: int) -> None:
        width = max(1, int(self.PICKET_WIDTH * post.scale))
        lean = height // 3
        canvas.line(self.PICKET, (post.x - lean, post.y), (post.x + lean, post.y - height), width=width)
        canvas.line(self.PICKET, (post.x + lean, post.y), (post.x - lean, post.y - height), width=width)

    def _draw_wire(self, canvas: Canvas, near: tuple[DepthPoint, int], far: tuple[DepthPoint, int]) -> None:
        (start, start_height), (end, end_height) = near, far
        for strand in self.STRANDS:
            canvas.line(self.WIRE, (start.x, start.y - start_height * strand), (end.x, end.y - end_height * strand))
