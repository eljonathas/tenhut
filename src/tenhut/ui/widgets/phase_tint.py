from __future__ import annotations

from typing import ClassVar

from tenhut.core import Phase
from tenhut.game.painting import Rgb
from tenhut.ui.painting import UiPalette


class PhaseTint:
    """The colours that tell the phases apart."""

    LABELS: ClassVar[dict[Phase, Rgb]] = {
        Phase.WORK: UiPalette.SALMON,
        Phase.SHORT: UiPalette.YELLOW,
        Phase.LONG: UiPalette.YELLOW,
        Phase.VICTORY: UiPalette.YELLOW,
    }

    @classmethod
    def label(cls, phase: Phase) -> Rgb:
        return cls.LABELS.get(phase, UiPalette.CHALK)

    @staticmethod
    def progress(phase: Phase) -> Rgb:
        return UiPalette.PROGRESS_WORK if phase is Phase.WORK else UiPalette.GREEN
