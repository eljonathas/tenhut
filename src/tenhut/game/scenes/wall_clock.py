from __future__ import annotations

import math
import time
from typing import ClassVar

from tenhut.core import Clock

from ..painting import Canvas, Palette, Rgb


class WallClock:
    """A small analogue clock that shows the real local time."""

    FACE: ClassVar[Rgb] = Rgb(250, 248, 236)
    MINUTE_HAND: ClassVar[Rgb] = Rgb(200, 40, 40)
    RIM_RADIUS: ClassVar[int] = 6
    FACE_RADIUS: ClassVar[int] = 5
    HOUR_HAND_LENGTH: ClassVar[int] = 3
    MINUTE_HAND_LENGTH: ClassVar[int] = 4
    HOURS_ON_DIAL: ClassVar[int] = 12
    MINUTES_PER_DIAL: ClassVar[int] = 720

    def __init__(self, center: tuple[int, int], clock: Clock) -> None:
        self._center = center
        self._clock = clock

    def draw(self, canvas: Canvas) -> None:
        canvas.circle(Palette.OUTLINE, self._center, self.RIM_RADIUS)
        canvas.circle(self.FACE, self._center, self.FACE_RADIUS)
        local = time.localtime(self._clock.now())
        hour_turn = local.tm_hour % self.HOURS_ON_DIAL / self.HOURS_ON_DIAL + local.tm_min / self.MINUTES_PER_DIAL
        self._draw_hand(canvas, hour_turn, length=self.HOUR_HAND_LENGTH, color=Palette.OUTLINE)
        self._draw_hand(canvas, local.tm_min / 60, length=self.MINUTE_HAND_LENGTH, color=self.MINUTE_HAND)

    def _draw_hand(self, canvas: Canvas, turn: float, *, length: int, color: Rgb) -> None:
        """``turn`` is the fraction of a full revolution clockwise from twelve o'clock."""
        angle = turn * math.tau - math.pi / 2
        cx, cy = self._center
        canvas.line(color, self._center, (cx + round(math.cos(angle) * length), cy + round(math.sin(angle) * length)))
