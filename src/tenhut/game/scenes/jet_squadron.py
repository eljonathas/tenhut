from __future__ import annotations

import math
from dataclasses import dataclass
from typing import ClassVar

import pygame

from ..geometry import Point
from ..painting import Canvas, Rgb
from .jet import Jet
from .parade_frame import ParadeFrame


@dataclass(slots=True)
class _Flight:
    x: float
    direction: int
    y: float
    speed: float
    phase: float


class _Trail:
    __slots__ = ("age", "x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.age = 0.0


class JetSquadron:
    """Five stunt planes in a V crossing the sky now and then, trailing white smoke behind buildings and banners."""

    FORMATION: ClassVar[tuple[Point, ...]] = (
        Point(0, 0),
        Point(-14, -6),
        Point(-14, 6),
        Point(-28, -12),
        Point(-28, 12),
    )
    SMOKE_LIFE: ClassVar[float] = 3.2
    SMOKE: ClassVar[Rgb] = Rgb(250, 250, 252)
    FIRST_LAUNCH_DELAY: ClassVar[float] = 3.0
    # The planes move one fixed 1/30 s step per drawn frame, as the animation was tuned to a 30 fps loop.
    FRAME_STEP: ClassVar[float] = 1 / 30
    EXIT_MARGIN: ClassVar[int] = 60
    START_MARGIN: ClassVar[int] = 30
    FORMATION_SQUASH: ClassVar[float] = 0.8
    WAVE_RATE: ClassVar[float] = 1.2
    WAVE_HEIGHT: ClassVar[float] = 3
    TAIL_GAP: ClassVar[int] = 6
    SINK_SPEED: ClassVar[float] = 1.5
    TRANSPARENT: ClassVar[tuple[int, int, int, int]] = (0, 0, 0, 0)

    def __init__(self) -> None:
        self._flight: _Flight | None = None
        self._trails: list[_Trail] = []
        self._next_launch_at: float | None = None
        self._layer: pygame.Surface | None = None

    def draw(self, canvas: Canvas, frame: ParadeFrame, sky_mask: pygame.Surface | None) -> None:
        size = canvas.surface.get_size()
        if self._next_launch_at is None:
            self._next_launch_at = frame.elapsed + self.FIRST_LAUNCH_DELAY
        if self._flight is None and frame.elapsed >= self._next_launch_at:
            self._launch(frame, size)
        jets = self._advance(frame.elapsed, size[0])
        if not self._trails and not jets:
            return
        layer = self._layer_of(size)
        layer_canvas = Canvas(layer)
        self._draw_trails(layer_canvas)
        for jet in jets:
            jet.draw(layer_canvas)
        if sky_mask is not None and sky_mask.get_size() == size:
            layer.blit(sky_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        canvas.surface.blit(layer, (0, 0))

    def _launch(self, frame: ParadeFrame, size: tuple[int, int]) -> None:
        width, height = size
        randomness = frame.randomness
        direction = randomness.choice((-1, 1))
        start = -self.START_MARGIN if direction > 0 else width + self.START_MARGIN
        self._flight = _Flight(
            start,
            direction,
            randomness.uniform(8, max(10, height * 0.11)),
            randomness.uniform(48, 60),
            randomness.uniform(0, 6),
        )
        pause = randomness.uniform(10, 16) if frame.party else randomness.uniform(18, 30)
        self._next_launch_at = frame.elapsed + pause

    def _advance(self, elapsed: float, world_width: int) -> list[Jet]:
        flight = self._flight
        if flight is None:
            return []
        flight.x += flight.direction * flight.speed * self.FRAME_STEP
        lead_y = flight.y + math.sin(elapsed * self.WAVE_RATE + flight.phase) * self.WAVE_HEIGHT
        jets = []
        for slot in self.FORMATION:
            position = Point(flight.x + slot.x * flight.direction, lead_y + slot.y * self.FORMATION_SQUASH)
            jets.append(Jet(position, flight.direction))
            self._trails.append(_Trail(position.x - flight.direction * self.TAIL_GAP, position.y + 1))
        gone = flight.x > world_width + self.EXIT_MARGIN if flight.direction > 0 else flight.x < -self.EXIT_MARGIN
        if gone:
            self._flight = None
        return jets

    def _draw_trails(self, canvas: Canvas) -> None:
        for trail in self._trails:
            trail.age += self.FRAME_STEP
            trail.y += self.SINK_SPEED * self.FRAME_STEP
            fade = min(1.0, trail.age / self.SMOKE_LIFE)
            alpha = int(200 * (1 - fade) ** 1.5)
            if alpha > 0:
                canvas.circle(self.SMOKE.with_alpha(alpha), (int(trail.x), int(trail.y)), int(1 + fade * 3))
        self._trails = [trail for trail in self._trails if trail.age < self.SMOKE_LIFE]

    def _layer_of(self, size: tuple[int, int]) -> pygame.Surface:
        if self._layer is None or self._layer.get_size() != size:
            self._layer = pygame.Surface(size, pygame.SRCALPHA)
        self._layer.fill(self.TRANSPARENT)
        return self._layer
