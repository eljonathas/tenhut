from __future__ import annotations

import math

from tenhut.game.character import Character
from tenhut.game.painting import Canvas
from tenhut.ui.painting import UiPalette

from .general_overlay import GeneralOverlay


class WhistleNotes(GeneralOverlay):
    """The music notes rising while he whistles at the scenery."""

    NOTES = 2
    HEAD_SIZE = (3, 2)
    MIN_TURN = 0.9
    ORIGIN = (55, 42)
    START_DISTANCE = 26
    DRIFT = 14
    RISE = 18
    WOBBLE = 2
    WOBBLE_SPEED = 6
    CYCLE_SPEED = 0.6
    NOTE_SPACING = 0.5

    def __init__(self, general: Character) -> None:
        self._general = general

    def applies(self) -> bool:
        return self._general.distracted and abs(self._general.facing) > self.MIN_TURN

    def draw(self, canvas: Canvas) -> None:
        general = self._general
        origin_x, origin_y = self.ORIGIN
        for index in range(self.NOTES):
            phase = (general.elapsed * self.CYCLE_SPEED + index * self.NOTE_SPACING) % 1.0
            x = origin_x + general.facing_direction * (self.START_DISTANCE + int(phase * self.DRIFT))
            y = (
                origin_y
                - int(phase * self.RISE)
                + int(self.WOBBLE * math.sin(general.elapsed * self.WOBBLE_SPEED + index))
            )
            canvas.rect(UiPalette.INK, (x + 2, y - 5, 1, 6))
            canvas.rect(UiPalette.INK, (x + 2, y - 5, 3, 1))
            canvas.rect(UiPalette.INK, (x, y, *self.HEAD_SIZE))
