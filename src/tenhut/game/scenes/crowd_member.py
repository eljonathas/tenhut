from __future__ import annotations

import math
from dataclasses import dataclass
from typing import ClassVar

from ..painting import Canvas, Palette, Rgb
from .bounce import Bounce
from .parade_frame import ParadeFrame


@dataclass(frozen=True, slots=True)
class CrowdMember:
    """One spectator on the pavement: a coloured shirt, a head, hair and, when cheering, a waving arm."""

    x: float
    y: float
    scale: float
    shirt: Rgb
    hair: Rgb
    phase: float

    SKIN: ClassVar[Rgb] = Rgb(232, 186, 140)
    PARTY_BOUNCE: ClassVar[Bounce] = Bounce(7, 4)
    CALM_BOUNCE: ClassVar[Bounce] = Bounce(3, 1.5)
    WAVE_RATE: ClassVar[float] = 9
    MIN_WAVING_SCALE: ClassVar[float] = 0.2

    def draw(self, canvas: Canvas, frame: ParadeFrame, waving: bool) -> None:
        bounce = self.PARTY_BOUNCE if frame.party else self.CALM_BOUNCE
        jump = abs(math.sin(frame.elapsed * bounce.rate + self.phase)) * bounce.height * self.scale * 2
        body_width, body_height = max(2, int(7 * self.scale)), max(3, int(12 * self.scale))
        head_radius = max(1, int(3 * self.scale))
        left, top = int(self.x - body_width / 2), int(self.y - body_height - jump)
        canvas.rect(Palette.OUTLINE, (left - 1, top - 1, body_width + 2, body_height + 1))
        canvas.rect(self.shirt, (left, top, body_width, body_height))
        self._draw_head(canvas, top, head_radius)
        if waving and self.scale > self.MIN_WAVING_SCALE:
            self._draw_arm(canvas, frame.elapsed, (left + body_width, top))

    def _draw_head(self, canvas: Canvas, body_top: int, radius: int) -> None:
        center = (int(self.x), body_top - radius)
        canvas.circle(Palette.OUTLINE, center, radius + 1)
        canvas.circle(self.SKIN, center, radius)
        canvas.rect(self.hair, (int(self.x) - radius, body_top - 2 * radius, 2 * radius, max(1, radius // 2 + 1)))

    def _draw_arm(self, canvas: Canvas, elapsed: float, shoulder: tuple[int, int]) -> None:
        wave = math.sin(elapsed * self.WAVE_RATE + self.phase) * 2 * self.scale
        hand = (shoulder[0] + 2 * self.scale + wave, shoulder[1] - 5 * self.scale)
        canvas.line(Palette.OUTLINE, (shoulder[0], shoulder[1] + 1), hand, width=max(1, int(2 * self.scale)))
