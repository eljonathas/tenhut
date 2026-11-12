from __future__ import annotations

from typing import ClassVar

from tenhut.controllers.severity import Severity
from tenhut.game.painting import Rgb
from tenhut.ui.painting import UiPalette


class SeverityTint:
    """The colour of each kind of status line."""

    COLORS: ClassVar[dict[Severity, Rgb]] = {
        Severity.NOTICE: UiPalette.YELLOW,
        Severity.SUCCESS: UiPalette.MINT,
        Severity.WARNING: UiPalette.PEACH,
        Severity.MUTED: UiPalette.CHALK_DIM,
        Severity.ALERT: UiPalette.CORAL,
    }

    @classmethod
    def of(cls, severity: Severity) -> Rgb:
        return cls.COLORS[severity]
