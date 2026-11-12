from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ..painting import Canvas, Rgb
from ..random_source import RandomSource


@dataclass(slots=True)
class _Cloud:
    x: float
    height_share: float
    speed: float
    size: int


class Clouds:
    """Slow clouds drifting right and wrapping around; shared by every outdoor scene."""

    COUNT: ClassVar[int] = 7
    WRAP_MARGIN: ClassVar[int] = 30
    RESPAWN_X: ClassVar[int] = -40
    LENGTH_PER_SIZE: ClassVar[int] = 18
    BODY_HEIGHT_PER_SIZE: ClassVar[int] = 6
    PUFF_HEIGHT_PER_SIZE: ClassVar[int] = 7
    PUFF_RISE_PER_SIZE: ClassVar[int] = 3
    PUFF_OFFSET: ClassVar[float] = 0.25
    PUFF_LENGTH: ClassVar[float] = 0.5

    def __init__(self, randomness: RandomSource) -> None:
        self._clouds = [
            _Cloud(
                randomness.uniform(0, 600),
                randomness.uniform(0.05, 0.45),
                randomness.uniform(2, 5),
                randomness.choice((1, 2)),
            )
            for _ in range(self.COUNT)
        ]

    def drift(self, dt: float, world_width: int) -> None:
        for cloud in self._clouds:
            cloud.x += cloud.speed * dt
            if cloud.x > world_width + self.WRAP_MARGIN:
                cloud.x = self.RESPAWN_X

    def draw(self, canvas: Canvas, horizon_y: int, color: Rgb) -> None:
        for cloud in self._clouds:
            y = cloud.height_share * horizon_y
            length = self.LENGTH_PER_SIZE * cloud.size
            size = cloud.size
            canvas.ellipse(color, (cloud.x, y, length, self.BODY_HEIGHT_PER_SIZE * size))
            puff = (
                cloud.x + length * self.PUFF_OFFSET,
                y - self.PUFF_RISE_PER_SIZE * size,
                length * self.PUFF_LENGTH,
                self.PUFF_HEIGHT_PER_SIZE * size,
            )
            canvas.ellipse(color, puff)
