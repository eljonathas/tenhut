from __future__ import annotations

from typing import ClassVar

from ..painting import Canvas, Palette, Rgb


class NotePad:
    """A yellow memo pad with scribbles and a pencil lying beside it."""

    PAPER: ClassVar[Rgb] = Rgb(250, 226, 110)
    SCRIBBLE: ClassVar[Rgb] = Rgb(180, 150, 60)
    PENCIL: ClassVar[Rgb] = Rgb(240, 190, 60)
    GRAPHITE: ClassVar[Rgb] = Rgb(60, 50, 40)

    def __init__(self, left: int, top: int) -> None:
        self._left = left
        self._top = top

    def draw(self, canvas: Canvas) -> None:
        x, y = self._left, self._top
        canvas.rect(Palette.OUTLINE, (x - 1, y + 5, 14, 12))
        canvas.rect(self.PAPER, (x, y + 6, 12, 10))
        canvas.line(self.SCRIBBLE, (x + 2, y + 9), (x + 9, y + 9))
        canvas.line(self.SCRIBBLE, (x + 2, y + 12), (x + 7, y + 12))
        canvas.line(Palette.OUTLINE, (x - 2, y + 21), (x + 12, y + 18), width=3)
        canvas.line(self.PENCIL, (x - 1, y + 20), (x + 10, y + 18))
        canvas.pixel(self.GRAPHITE, (x + 12, y + 18))
