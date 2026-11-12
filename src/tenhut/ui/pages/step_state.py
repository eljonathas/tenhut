from __future__ import annotations

from enum import Enum

from tenhut.game.painting import Rgb
from tenhut.ui.painting import UiPalette


class StepState(Enum):
    """Where a calibration step stands: done, being asked for now, or still to come."""

    DONE = ("✓ ", UiPalette.CHALK_DIM)
    CURRENT = ("> ", UiPalette.YELLOW)
    PENDING = ("  ", UiPalette.CHALK)

    @property
    def mark(self) -> str:
        return self.value[0]

    @property
    def color(self) -> Rgb:
        return self.value[1]

    @classmethod
    def of(cls, index: int, current: int) -> StepState:
        if index < current:
            return cls.DONE
        return cls.CURRENT if index == current else cls.PENDING
