from __future__ import annotations

import math
from dataclasses import dataclass
from typing import ClassVar

from ..painting import Canvas, Rgb
from .ambient_frame import AmbientFrame


@dataclass(slots=True)
class _Bird:
    x: float
    y: float
    velocity: float


class Birds:
    """Occasional flocks of one or three birds crossing the sky, drawn as flapping pixel chevrons."""

    FIRST_FLOCK_AT: ClassVar[float] = 5.0
    FLOCK_SIZES: ClassVar[tuple[int, ...]] = (1, 1, 3)
    LOW_SPEED: ClassVar[float] = 22
    HIGH_SPEED: ClassVar[float] = 30
    SPAWN_MARGIN: ClassVar[int] = 6
    FLOCK_SPACING_X: ClassVar[int] = 7
    FLOCK_SPACING_Y: ClassVar[int] = 4
    DESPAWN_MARGIN: ClassVar[int] = 60
    COLOR: ClassVar[Rgb] = Rgb(40, 40, 52)
    FLAP_RATE: ClassVar[float] = 6
    BOB_RATE: ClassVar[float] = 2
    HEIGHT_CEILING: ClassVar[int] = 4

    def __init__(self) -> None:
        self._flock: list[_Bird] = []
        self._next_flock_at = self.FIRST_FLOCK_AT

    def fly(self, dt: float, frame: AmbientFrame) -> None:
        if frame.elapsed >= self._next_flock_at:
            self._launch(frame)
        for bird in self._flock:
            bird.x += bird.velocity * dt
        width = frame.world_width
        self._flock = [bird for bird in self._flock if -self.DESPAWN_MARGIN < bird.x < width + self.DESPAWN_MARGIN]

    def _launch(self, frame: AmbientFrame) -> None:
        width, randomness = frame.world_width, frame.randomness
        direction = randomness.choice((-1, 1))
        y = randomness.uniform(10, max(20, frame.world_height * 0.3))
        for index in range(randomness.choice(self.FLOCK_SIZES)):
            x = (
                (-self.SPAWN_MARGIN - index * self.FLOCK_SPACING_X)
                if direction > 0
                else (width + self.SPAWN_MARGIN + index * self.FLOCK_SPACING_X)
            )
            self._flock.append(
                _Bird(
                    x, y + index * self.FLOCK_SPACING_Y, direction * randomness.uniform(self.LOW_SPEED, self.HIGH_SPEED)
                )
            )
        self._next_flock_at = frame.elapsed + randomness.uniform(14, 40)

    def draw(self, canvas: Canvas, horizon_y: int, elapsed: float) -> None:
        width, height = canvas.surface.get_size()
        for bird in self._flock:
            wings_up = int(elapsed * self.FLAP_RATE + bird.x * 0.1) % 2
            y = int(
                min(bird.y, horizon_y - self.HEIGHT_CEILING) + math.sin(elapsed * self.BOB_RATE + bird.x * 0.05) * 2
            )
            for reach in (1, 2):
                for side in (-reach, reach):
                    px, py = int(bird.x) + side, y - (reach if wings_up else -reach + 1)
                    if 0 <= px < width and 0 <= py < height:
                        canvas.pixel(self.COLOR, (px, py))
