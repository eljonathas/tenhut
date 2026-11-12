from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ..painting import Canvas, Rgb
from .ambient_frame import AmbientFrame


@dataclass(slots=True)
class _Puff:
    x: float
    y: float
    radius: float
    life: float


class SmokeDrift:
    """Grey smoke rising over the battlefield and thickening as it fades."""

    RISE_SPEED: ClassVar[float] = 6
    DRIFT_SPEED: ClassVar[float] = 3
    GROWTH_SPEED: ClassVar[float] = 2.5
    START_RADIUS: ClassVar[float] = 2.0
    MAX_LIFE: ClassVar[float] = 7
    BASE_GREY: ClassVar[int] = 120
    GREY_RANGE: ClassVar[int] = 60
    BLUE_TINT: ClassVar[int] = 6

    def __init__(self) -> None:
        self._puffs: list[_Puff] = []
        self._next_puff_at = 0.0

    def rise(self, dt: float) -> None:
        for puff in self._puffs:
            puff.y -= self.RISE_SPEED * dt
            puff.x += self.DRIFT_SPEED * dt
            puff.radius += self.GROWTH_SPEED * dt
            puff.life -= dt
        self._puffs = [puff for puff in self._puffs if puff.life > 0]

    def emit_if_due(self, frame: AmbientFrame, horizon_y: int) -> None:
        """Release a puff somewhere along the horizon line."""
        if frame.elapsed >= self._next_puff_at:
            randomness = frame.randomness
            self._puffs.append(
                _Puff(randomness.uniform(0, frame.world_width), horizon_y, self.START_RADIUS, randomness.uniform(4, 7))
            )
            self._next_puff_at = frame.elapsed + randomness.uniform(0.6, 1.6)

    def draw(self, canvas: Canvas) -> None:
        for puff in self._puffs:
            grey = int(self.BASE_GREY + self.GREY_RANGE * (1 - puff.life / self.MAX_LIFE))
            canvas.circle(Rgb(grey, grey, grey + self.BLUE_TINT), (int(puff.x), int(puff.y)), int(puff.radius))
