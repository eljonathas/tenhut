from __future__ import annotations

from dataclasses import dataclass

from tenhut.game.painting import Rgb


@dataclass(frozen=True, slots=True)
class BarFill:
    """How full a progress bar is, and the colour of the filled part."""

    fraction: float
    color: Rgb
