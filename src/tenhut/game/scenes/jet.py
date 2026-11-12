from __future__ import annotations

from typing import ClassVar

from ..geometry import Point
from ..painting import Canvas, Palette, Rgb


class Jet:
    """A side-view stunt plane about 13x5 pixels, nose pointing in its flight direction (+1 right, -1 left)."""

    HULL: ClassVar[Rgb] = Rgb(240, 242, 246)
    STRIPE: ClassVar[Rgb] = Rgb(40, 90, 170)
    RUDDER: ClassVar[Rgb] = Rgb(220, 60, 60)
    WING: ClassVar[Rgb] = Rgb(60, 70, 90)
    CANOPY: ClassVar[Rgb] = Rgb(120, 180, 230)
    HULL_OUTLINE: ClassVar[tuple[tuple[int, int], ...]] = ((6, 0), (4, -1), (-5, -1), (-6, 0), (-5, 1), (4, 1))
    NOSE_VERTICES: ClassVar[int] = 2

    def __init__(self, position: Point, direction: int) -> None:
        self._x = int(position.x)
        self._y = int(position.y)
        self._direction = direction

    def draw(self, canvas: Canvas) -> None:
        hull = [self._at(dx, dy) for dx, dy in self.HULL_OUTLINE]
        shadow = [
            (px + (1 if index < self.NOSE_VERTICES else 0) * self._direction, py) for index, (px, py) in enumerate(hull)
        ]
        canvas.polygon(Palette.OUTLINE, shadow)
        canvas.polygon(self.HULL, hull)
        canvas.line(self.STRIPE, self._at(-5, 0), self._at(5, 0))
        canvas.polygon(Palette.OUTLINE, [self._at(-4, -1), self._at(-6, -4), self._at(-3, -1)])
        canvas.line(self.RUDDER, self._at(-5, -2), self._at(-5, -3))
        canvas.line(self.WING, self._at(-1, 1), self._at(2, 1))
        canvas.pixel(self.CANOPY, self._at(3, -1))
        canvas.pixel(self.CANOPY, self._at(2, -1))

    def _at(self, forward: int, up: int) -> tuple[int, int]:
        """A pixel ``forward`` of the centre (mirrored for planes flying left) and ``up`` below it."""
        return self._x + forward * self._direction, self._y + up
