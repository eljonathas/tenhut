from __future__ import annotations

from typing import ClassVar

from ..painting import Canvas, Palette, Rgb


class Radio:
    """A field radio with a speaker dial and an antenna."""

    CASE: ClassVar[Rgb] = Rgb(70, 80, 60)
    SCREEN: ClassVar[Rgb] = Rgb(30, 40, 30)
    KNOB: ClassVar[Rgb] = Rgb(200, 200, 190)

    def __init__(self, left: int, desk_y: int) -> None:
        self._left = left
        self._desk_y = desk_y

    def draw(self, canvas: Canvas) -> None:
        x, y = self._left, self._desk_y
        canvas.rect(Palette.OUTLINE, (x - 1, y + 3, 17, 13))
        canvas.rect(self.CASE, (x, y + 4, 15, 11))
        canvas.rect(self.SCREEN, (x + 2, y + 6, 6, 4))
        canvas.circle(self.KNOB, (x + 11, y + 10), 2)
        canvas.line(Palette.OUTLINE, (x + 13, y + 4), (x + 16, y - 9))
