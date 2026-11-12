from __future__ import annotations

from typing import ClassVar

from ..painting import Canvas, Palette, Rgb


class DeskPlaque:
    """The general's brass nameplate on the near edge of the desk."""

    WOOD: ClassVar[Rgb] = Rgb(88, 60, 36)
    BRASS: ClassVar[Rgb] = Rgb(230, 190, 80)
    ENGRAVING: ClassVar[Rgb] = Rgb(120, 90, 40)
    ENGRAVING_STEP: ClassVar[int] = 3
    ENGRAVING_LENGTH: ClassVar[int] = 20

    def __init__(self, center_x: int, desk_y: int) -> None:
        self._center_x = center_x
        self._desk_y = desk_y

    def draw(self, canvas: Canvas) -> None:
        x, y = self._center_x, self._desk_y
        canvas.rect(Palette.OUTLINE, (x - 15, y - 5, 30, 7))
        canvas.rect(self.WOOD, (x - 14, y - 4, 28, 5))
        canvas.rect(self.BRASS, (x - 11, y - 3, 22, 3))
        for dash in range(0, self.ENGRAVING_LENGTH, self.ENGRAVING_STEP):
            canvas.pixel(self.ENGRAVING, (x - 10 + dash, y - 2))
