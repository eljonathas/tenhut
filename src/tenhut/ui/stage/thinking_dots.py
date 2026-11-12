from __future__ import annotations

from tenhut.controllers.judge_slot import JudgeSlot
from tenhut.core import Clock
from tenhut.game.painting import Canvas
from tenhut.ui.painting import UiPalette

from .general_overlay import GeneralOverlay


class ThinkingDots(GeneralOverlay):
    """The dots growing beside his head while he waits for the judge."""

    DOTS = 4
    SPACING = 4
    RISE = 2
    SIZE = 2
    SPEED = 3
    ORIGIN = (76, 14)

    def __init__(self, judge: JudgeSlot, clock: Clock) -> None:
        self._judge = judge
        self._clock = clock

    def applies(self) -> bool:
        return self._judge.active

    def draw(self, canvas: Canvas) -> None:
        x, y = self.ORIGIN
        for index in range(int(self._clock.now() * self.SPEED) % self.DOTS):
            canvas.rect(UiPalette.THOUGHT, (x + index * self.SPACING, y - index * self.RISE, self.SIZE, self.SIZE))
