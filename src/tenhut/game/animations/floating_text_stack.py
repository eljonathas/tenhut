from __future__ import annotations

import pygame

from tenhut.game.geometry import Point
from tenhut.game.global_random import GlobalRandom
from tenhut.game.painting import Palette, Rgb
from tenhut.game.random_source import RandomSource

from .animation import Animation
from .floating_text import FloatingText


class FloatingTextStack(Animation):
    """Every floating message currently on screen; new ones start a line above the older ones."""

    SPREAD = 8
    FIRST_LINE = -10
    LINE_HEIGHT = 16

    def __init__(self, font: pygame.font.Font, randomness: RandomSource | None = None) -> None:
        self._font = font
        self._randomness = randomness or GlobalRandom()
        self._messages: list[FloatingText] = []
        self._anchor = Point(0, 0)

    @property
    def finished(self) -> bool:
        return not self._messages

    def pop_up(self, message: str, color: Rgb = Palette.GOLD_LIGHT) -> None:
        drift = self._randomness.randint(-self.SPREAD, self.SPREAD)
        line = self.FIRST_LINE - self.LINE_HEIGHT * len(self._messages)
        self._messages.append(FloatingText(message, color, self._font, Point(drift, line)))

    def anchor_at(self, anchor: Point) -> None:
        self._anchor = anchor

    def update(self, dt: float) -> None:
        for message in self._messages:
            message.update(dt)
        self._messages = [message for message in self._messages if not message.finished]

    def draw(self, surface: pygame.Surface) -> None:
        for message in self._messages:
            message.anchor_at(self._anchor)
            message.draw(surface)
