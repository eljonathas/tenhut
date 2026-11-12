from __future__ import annotations

from typing import ClassVar

from ..painting import Canvas, Rgb


class DeadTree:
    """A bare tree standing on the horizon: a trunk and two stumpy branches."""

    BARK: ClassVar[Rgb] = Rgb(60, 50, 46)
    ROOT_DEPTH: ClassVar[int] = 1
    TRUNK_HEIGHT: ClassVar[int] = 16

    def __init__(self, x: int, horizon_y: int) -> None:
        self._x = x
        self._horizon_y = horizon_y

    def draw(self, canvas: Canvas) -> None:
        x, y = self._x, self._horizon_y
        canvas.line(self.BARK, (x, y + self.ROOT_DEPTH), (x, y - self.TRUNK_HEIGHT), width=2)
        canvas.line(self.BARK, (x, y - 9), (x - 5, y - 14))
        canvas.line(self.BARK, (x, y - 12), (x + 4, y - 18))
