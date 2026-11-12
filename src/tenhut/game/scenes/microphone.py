from __future__ import annotations

from typing import ClassVar

from ..painting import Canvas, Palette, Rgb


class Microphone:
    """A stand microphone in front of the general, below his face."""

    STAND: ClassVar[Rgb] = Rgb(150, 150, 160)
    HEAD: ClassVar[Rgb] = Rgb(70, 70, 80)
    GRILLE: ClassVar[Rgb] = Rgb(140, 140, 150)

    def __init__(self, x: int, base_y: int) -> None:
        self._x = x
        self._base_y = base_y

    def draw(self, canvas: Canvas) -> None:
        x, y = self._x, self._base_y
        canvas.line(Palette.OUTLINE, (x, y + 4), (x, y - 20), width=3)
        canvas.line(self.STAND, (x, y + 4), (x, y - 20))
        canvas.ellipse(Palette.OUTLINE, (x - 4, y - 28, 8, 10))
        canvas.ellipse(self.HEAD, (x - 3, y - 27, 6, 8))
        for grille_y in range(y - 26, y - 19, 2):
            canvas.line(self.GRILLE, (x - 2, grille_y), (x + 2, grille_y))
