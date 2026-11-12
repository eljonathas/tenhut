from __future__ import annotations

import pygame

from tenhut.game.geometry import Point
from tenhut.game.painting import Palette, Rgb

from .animation import Animation
from .lettering import Lettering


class FloatingText(Animation):
    """A short message that drifts upwards from its anchor and disappears (+1 XP, +5 min...)."""

    LIFETIME = 2.2
    RISE_SPEED = 28
    SHADOW_OFFSET = 1

    def __init__(self, message: str, color: Rgb, font: pygame.font.Font, start: Point) -> None:
        self._message = message
        self._color = color
        self._lettering = Lettering(font)
        self._position = start
        self._age = 0.0
        self._anchor = Point(0, 0)

    @property
    def finished(self) -> bool:
        return self._age >= self.LIFETIME

    def anchor_at(self, anchor: Point) -> None:
        """The point the message's own offset is measured from."""
        self._anchor = anchor

    def update(self, dt: float) -> None:
        self._age += dt
        self._position = self._position.moved(dy=-self.RISE_SPEED * dt)

    def draw(self, surface: pygame.Surface) -> None:
        x = self._anchor.x + int(self._position.x)
        y = self._anchor.y + int(self._position.y)
        shadow = Point(x + self.SHADOW_OFFSET, y + self.SHADOW_OFFSET)
        self._lettering.draw_centered(surface, self._message, shadow, Palette.OUTLINE)
        self._lettering.draw_centered(surface, self._message, Point(x, y), self._color)
