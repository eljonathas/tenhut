from __future__ import annotations

from typing import ClassVar

from ..painting import Canvas, Palette, Rgb


class FlagPole:
    """A steel pole with a gold ball on top."""

    SHAFT: ClassVar[Rgb] = Rgb(196, 196, 206)
    OUTLINE_WIDTH: ClassVar[int] = 4
    SHAFT_WIDTH: ClassVar[int] = 2
    FINIAL_RADIUS: ClassVar[int] = 2

    def __init__(self, x: int, top: int, bottom: int) -> None:
        self._x = x
        self._top = top
        self._bottom = bottom

    def draw(self, canvas: Canvas) -> None:
        length = self._bottom - self._top
        canvas.rect(Palette.OUTLINE, (self._x - 1, self._top, self.OUTLINE_WIDTH, length))
        canvas.rect(self.SHAFT, (self._x, self._top + 1, self.SHAFT_WIDTH, length - 1))
        canvas.circle(Palette.GOLD, (self._x + 1, self._top - 1), self.FINIAL_RADIUS)
