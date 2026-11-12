from __future__ import annotations

import math
from typing import ClassVar

from ..painting import Canvas, Rgb


class MountainRange:
    """A silhouette of rolling hills along a base line."""

    STEP: ClassVar[int] = 10
    SKIRT: ClassVar[int] = 10
    MAIN_SHARE: ClassVar[float] = 0.6
    SWELL_SHARE: ClassVar[float] = 0.4
    RIPPLE_HEIGHT: ClassVar[int] = 5
    RIPPLE_FREQUENCY: ClassVar[float] = 0.13

    def __init__(self, color: Rgb, amplitude: int, *, frequency: float = 0.045, offset: int = 0) -> None:
        self._color = color
        self._amplitude = amplitude
        self._frequency = frequency
        self._offset = offset

    def paint(self, canvas: Canvas, width: int, base: int) -> None:
        points = [(0, base + self.SKIRT)]
        for x in range(0, width + 2 * self.STEP, self.STEP):
            points.append((x, base - int(self._height_at(x))))
        points.append((width, base + self.SKIRT))
        canvas.polygon(self._color, points)

    def _height_at(self, x: int) -> float:
        swell = self._amplitude * (self.MAIN_SHARE + self.SWELL_SHARE * math.sin(x * self._frequency + self._offset))
        return swell + self.RIPPLE_HEIGHT * math.sin(x * self.RIPPLE_FREQUENCY + self._offset * 2)
