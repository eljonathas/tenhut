from __future__ import annotations

from typing import ClassVar

from ..painting import Canvas, Palette, Rgb


class Helmet:
    """A steel helmet left on the parapet."""

    STEEL: ClassVar[Rgb] = Rgb(84, 104, 60)
    SHINE: ClassVar[Rgb] = Rgb(120, 144, 90)
    REACH: ClassVar[int] = 18

    def __init__(self, left: int, parapet_y: int) -> None:
        self._left = left
        self._parapet_y = parapet_y

    def draw(self, canvas: Canvas) -> None:
        x, top = self._left, self._parapet_y
        canvas.ellipse(Palette.OUTLINE, (x - 1, top - 9, 18, 11))
        canvas.ellipse(self.STEEL, (x, top - 8, 16, 10))
        canvas.rect(Palette.OUTLINE, (x - 3, top - 2, 22, 3))
        canvas.rect(self.STEEL, (x - 2, top - 2, 20, 2))
        canvas.line(self.SHINE, (x + 4, top - 6), (x + 9, top - 7))
