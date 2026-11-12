from __future__ import annotations

import math
from dataclasses import dataclass
from typing import ClassVar

from ..painting import Canvas, Rgb
from .ambient_frame import AmbientFrame


@dataclass(slots=True)
class _Spark:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    color: Rgb


class FireworkShow:
    """Rocket bursts for the victory sky: each one throws a ring of sparks that arc down and fade."""

    SPARKS_PER_BURST: ClassVar[int] = 28
    GRAVITY: ClassVar[float] = 30
    DIM_LIFE: ClassVar[float] = 0.4
    WIDE_LIFE: ClassVar[float] = 0.7
    DIM_FACTOR: ClassVar[float] = 0.6
    COLORS: ClassVar[tuple[Rgb, ...]] = (
        Rgb(255, 110, 100),
        Rgb(255, 226, 110),
        Rgb(130, 220, 255),
        Rgb(170, 255, 150),
        Rgb(255, 160, 230),
    )

    def __init__(self) -> None:
        self._sparks: list[_Spark] = []
        self._next_burst_at = 0.0
        self._launching = False

    @property
    def launching(self) -> bool:
        return self._launching

    @launching.setter
    def launching(self, value: bool) -> None:
        self._launching = value

    def update(self, dt: float, frame: AmbientFrame) -> None:
        for spark in self._sparks:
            spark.x += spark.vx * dt
            spark.y += spark.vy * dt
            spark.vy += self.GRAVITY * dt
            spark.life -= dt
        self._sparks = [spark for spark in self._sparks if spark.life > 0]
        if self._launching and frame.elapsed >= self._next_burst_at:
            self._explode(frame)
            self._next_burst_at = frame.elapsed + frame.randomness.uniform(0.5, 1.4)

    def _explode(self, frame: AmbientFrame) -> None:
        width, height, randomness = frame.world_width, frame.world_height, frame.randomness
        x, y = randomness.uniform(width * 0.1, width * 0.9), randomness.uniform(height * 0.08, height * 0.35)
        color = randomness.choice(self.COLORS)
        for index in range(self.SPARKS_PER_BURST):
            angle = index / self.SPARKS_PER_BURST * math.tau
            speed = randomness.uniform(22, 38)
            self._sparks.append(
                _Spark(x, y, math.cos(angle) * speed, math.sin(angle) * speed, randomness.uniform(0.8, 1.3), color)
            )

    def draw(self, canvas: Canvas) -> None:
        width, height = canvas.surface.get_size()
        for spark in self._sparks:
            if 0 <= spark.x < width and 0 <= spark.y < height:
                color = spark.color if spark.life > self.DIM_LIFE else spark.color.shaded(self.DIM_FACTOR)
                x, y = int(spark.x), int(spark.y)
                canvas.pixel(color, (x, y))
                if spark.life > self.WIDE_LIFE and 0 <= x + 1 < width:
                    canvas.pixel(color, (x + 1, y))
