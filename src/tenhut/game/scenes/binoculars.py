from __future__ import annotations

from typing import ClassVar

from ..painting import Canvas, Palette, Rgb


class Binoculars:
    """Field glasses resting on the parapet."""

    BODY: ClassVar[Rgb] = Rgb(50, 50, 56)
    LENS: ClassVar[Rgb] = Rgb(120, 170, 220)
    BARREL_SPACING: ClassVar[int] = 7

    def __init__(self, left: int, parapet_y: int) -> None:
        self._left = left
        self._parapet_y = parapet_y

    def draw(self, canvas: Canvas) -> None:
        top = self._parapet_y
        for barrel in (0, self.BARREL_SPACING):
            x = self._left + barrel
            canvas.rect(Palette.OUTLINE, (x - 1, top - 8, 7, 9))
            canvas.rect(self.BODY, (x, top - 7, 5, 7))
            canvas.rect(self.LENS, (x + 1, top - 2, 3, 1))
        canvas.rect(self.BODY, (self._left + 4, top - 5, 4, 2))
