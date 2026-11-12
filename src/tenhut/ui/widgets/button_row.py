from __future__ import annotations

import pygame

from .button import Button
from .button_spec import ButtonSpec


class ButtonRow:
    """Shares a strip of the screen equally among buttons."""

    GAP = 4

    def __init__(self, area: pygame.Rect) -> None:
        self._area = area

    def build(self, specs: list[ButtonSpec]) -> list[Button]:
        count = len(specs)
        width = (self._area.w - self.GAP * (count - 1)) // count
        return [
            Button((self._area.x + index * (width + self.GAP), self._area.y, width, self._area.h), spec)
            for index, spec in enumerate(specs)
        ]
