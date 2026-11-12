from __future__ import annotations

import math

from tenhut.game.character import Character
from tenhut.game.painting import Canvas
from tenhut.ui.painting import UiPalette

from .general_overlay import GeneralOverlay


class AlertMark(GeneralOverlay):
    """The bouncing exclamation mark over his head when he spots the soldier."""

    ANCHOR = (80, 8)
    BOUNCE_HEIGHT = 3
    OUTLINE_WIDTH = 5
    OUTLINE_HEIGHT = 13
    BAR_WIDTH = 3
    BAR_HEIGHT = 7
    DOT_TOP = 9
    DOT_HEIGHT = 2
    BOUNCE_SPEED = 14

    def __init__(self, general: Character) -> None:
        self._general = general

    def applies(self) -> bool:
        return self._general.alerting

    def draw(self, canvas: Canvas) -> None:
        x, y = self.ANCHOR
        y -= int(self.BOUNCE_HEIGHT * abs(math.sin(self._general.elapsed * self.BOUNCE_SPEED)))
        canvas.rect(UiPalette.INK, (x - 1, y - 1, self.OUTLINE_WIDTH, self.OUTLINE_HEIGHT))
        canvas.rect(UiPalette.YELLOW, (x, y, self.BAR_WIDTH, self.BAR_HEIGHT))
        canvas.rect(UiPalette.YELLOW, (x, y + self.DOT_TOP, self.BAR_WIDTH, self.DOT_HEIGHT))
