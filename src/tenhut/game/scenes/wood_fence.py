from __future__ import annotations

from typing import ClassVar

from ..geometry import Point
from ..painting import Canvas, Palette, Rgb
from .depth_point import DepthPoint


class WoodFence:
    """A post-and-rail fence running toward the horizon."""

    POST: ClassVar[Rgb] = Rgb(150, 104, 60)
    RAIL: ClassVar[Rgb] = Rgb(120, 80, 46)
    POST_HEIGHT: ClassVar[int] = 22
    POST_WIDTH: ClassVar[int] = 3
    UPPER_RAIL: ClassVar[float] = 0.8
    LOWER_RAIL: ClassVar[float] = 0.4

    def __init__(self, posts: list[DepthPoint]) -> None:
        self._posts = posts

    def draw(self, canvas: Canvas) -> None:
        tops = [self._draw_post(canvas, post) for post in self._posts]
        if len(tops) > 1:
            canvas.lines(self.RAIL, tops)
            lower = [Point(top.x, post.y + self.LOWER_RAIL * (top.y - post.y)) for top, post in zip(tops, self._posts)]
            canvas.lines(self.RAIL, lower)

    def _draw_post(self, canvas: Canvas, post: DepthPoint) -> Point:
        height = max(2, int(self.POST_HEIGHT * post.scale))
        width = max(1, int(self.POST_WIDTH * post.scale))
        canvas.rect(Palette.OUTLINE, (post.x - width // 2 - 1, post.y - height - 1, width + 2, height + 2))
        canvas.rect(self.POST, (post.x - width // 2, post.y - height, width, height))
        return Point(post.x, post.y - height * self.UPPER_RAIL)
