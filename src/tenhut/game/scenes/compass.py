from __future__ import annotations

from typing import ClassVar

from ..painting import Canvas, Palette, Rgb


class Compass:
    """A brass compass lying on the map."""

    BRASS: ClassVar[Rgb] = Rgb(230, 200, 90)
    DIAL: ClassVar[Rgb] = Rgb(250, 250, 240)
    NORTH: ClassVar[Rgb] = Rgb(200, 40, 40)

    def __init__(self, center: tuple[int, int]) -> None:
        self._center = center

    def draw(self, canvas: Canvas) -> None:
        x, y = self._center
        canvas.circle(Palette.OUTLINE, self._center, 5)
        canvas.circle(self.BRASS, self._center, 4)
        canvas.circle(self.DIAL, self._center, 2)
        canvas.pixel(self.NORTH, (x, y - 2))
