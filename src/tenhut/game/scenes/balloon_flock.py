from __future__ import annotations

import math
from dataclasses import dataclass
from typing import ClassVar

from ..painting import Canvas, Palette, Rgb
from .parade_frame import ParadeFrame


@dataclass(slots=True)
class _Balloon:
    x: float
    y: float
    rise_speed: float
    sway_phase: float
    color: Rgb


class BalloonFlock:
    """Party balloons released every few seconds, swaying as they rise out of sight."""

    # Fixed 1/30 s per drawn frame, like the other parade objects.
    FRAME_STEP: ClassVar[float] = 1 / 30
    START_HEIGHT_SHARE: ClassVar[float] = 0.7
    GONE_ABOVE: ClassVar[int] = -12
    SWAY_RATE: ClassVar[float] = 1.3
    SWAY_REACH: ClassVar[float] = 2
    STRING: ClassVar[Rgb] = Rgb(90, 90, 90)
    GLINT: ClassVar[Rgb] = Rgb(255, 255, 255)
    COLORS: ClassVar[tuple[Rgb, ...]] = (Rgb(230, 70, 70), Rgb(250, 200, 70), Rgb(90, 140, 230), Rgb(120, 200, 120))

    def __init__(self) -> None:
        self._balloons: list[_Balloon] = []
        self._next_release_at = 0.0

    def draw(self, canvas: Canvas, frame: ParadeFrame) -> None:
        width, height = canvas.surface.get_size()
        randomness = frame.randomness
        if frame.elapsed >= self._next_release_at:
            self._balloons.append(
                _Balloon(
                    randomness.uniform(width * 0.05, width * 0.95),
                    height * self.START_HEIGHT_SHARE,
                    randomness.uniform(5, 9),
                    randomness.uniform(0, 6),
                    randomness.choice(self.COLORS),
                )
            )
            self._next_release_at = frame.elapsed + randomness.uniform(2.5, 6)
        for balloon in self._balloons:
            balloon.y -= balloon.rise_speed * self.FRAME_STEP
            self._draw_balloon(canvas, balloon, frame.elapsed)
        self._balloons = [balloon for balloon in self._balloons if balloon.y > self.GONE_ABOVE]

    def _draw_balloon(self, canvas: Canvas, balloon: _Balloon, elapsed: float) -> None:
        x = int(balloon.x + math.sin(elapsed * self.SWAY_RATE + balloon.sway_phase) * self.SWAY_REACH)
        y = int(balloon.y)
        canvas.line(self.STRING, (x, y + 4), (x + 1, y + 9))
        canvas.ellipse(Palette.OUTLINE, (x - 3, y - 4, 7, 9))
        canvas.ellipse(balloon.color, (x - 2, y - 3, 5, 7))
        canvas.pixel(self.GLINT, (x - 1, y - 2))
