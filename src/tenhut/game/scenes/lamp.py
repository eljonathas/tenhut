from __future__ import annotations

import math
from typing import ClassVar

from ..painting import Canvas, Palette, Rgb


class Lamp:
    """A green-shaded lamp swinging from the ceiling."""

    SHADE: ClassVar[Rgb] = Rgb(60, 92, 60)
    SWING: ClassVar[float] = 2
    SWING_SPEED: ClassVar[float] = 1.3

    def __init__(self, x: int, cord_top: int, cord_bottom: int) -> None:
        self._x = x
        self._top = cord_top
        self._bottom = cord_bottom

    def draw(self, canvas: Canvas, elapsed: float) -> None:
        bottom = self._bottom
        sway = int(self._x + math.sin(elapsed * self.SWING_SPEED) * self.SWING)
        canvas.line(Palette.OUTLINE, (self._x, self._top), (sway, bottom))
        canvas.polygon(
            Palette.OUTLINE,
            [(sway - 7, bottom + 6), (sway - 3, bottom - 1), (sway + 3, bottom - 1), (sway + 7, bottom + 6)],
        )
        canvas.polygon(
            self.SHADE, [(sway - 6, bottom + 5), (sway - 2, bottom), (sway + 2, bottom), (sway + 6, bottom + 5)]
        )
        canvas.rect(Palette.GOLD_LIGHT, (sway - 2, bottom + 5, 5, 2))
