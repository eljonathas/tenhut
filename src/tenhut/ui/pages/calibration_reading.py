from __future__ import annotations

from dataclasses import dataclass

from tenhut.game.painting import Rgb


@dataclass(frozen=True, slots=True)
class CalibrationReading:
    """How the calibration test words one camera reading: the big label, its colour and the verdict under it."""

    label_key: str
    color: Rgb
    verdict_key: str | None
