from __future__ import annotations

import pygame

from tenhut.game.global_random import GlobalRandom
from tenhut.game.painting import Canvas, Palette
from tenhut.game.random_source import RandomSource

from .animation import Animation


class CurtainTransition(Animation):
    """The new scene drops down over the old one in columns, each starting a little after its neighbour."""

    DURATION = 1.3
    STAGGER = 0.45
    JITTER = 0.15
    COLUMN_FALL_SHARE = 0.4
    EDGE_THICKNESS = 2

    def __init__(self, previous: pygame.Surface, column_width: int = 8, randomness: RandomSource | None = None) -> None:
        randomness = randomness or GlobalRandom()
        self._previous = previous
        self._column_width = column_width
        self._elapsed = 0.0
        columns = previous.get_width() // column_width + 1
        self._delays = [self.STAGGER * index / columns + randomness.uniform(0, self.JITTER) for index in range(columns)]

    @property
    def finished(self) -> bool:
        return self._elapsed >= self.DURATION

    def update(self, dt: float) -> None:
        self._elapsed += dt

    def draw(self, surface: pygame.Surface) -> None:
        """Covers the part of ``surface`` the old scene still hides; ends at once if the size changed."""
        if self._previous.get_size() != surface.get_size():
            self._elapsed = self.DURATION
            return
        width = surface.get_width()
        progress = self._elapsed / self.DURATION
        for index, delay in enumerate(self._delays):
            fall = max(0.0, min(1.0, (progress - delay) / self.COLUMN_FALL_SHARE))
            left = index * self._column_width
            if fall >= 1 or width - left <= 0:
                continue
            self._draw_column(surface, left, min(self._column_width, width - left), fall)

    def _draw_column(self, surface: pygame.Surface, left: int, column_width: int, fall: float) -> None:
        height = surface.get_height()
        top = int(fall * fall * height)
        surface.blit(self._previous, (left, top), (left, top, column_width, height - top))
        if fall > 0:
            Canvas(surface).rect(Palette.OUTLINE, (left, top - self.EDGE_THICKNESS, column_width, self.EDGE_THICKNESS))
