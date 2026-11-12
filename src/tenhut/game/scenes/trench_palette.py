from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ..painting import Rgb


@dataclass(frozen=True, slots=True)
class TrenchPalette:
    """Mud colours of the front line, by day or by night."""

    mud: Rgb
    mud_alt: Rgb

    DAY: ClassVar[TrenchPalette]
    NIGHT: ClassVar[TrenchPalette]


TrenchPalette.DAY = TrenchPalette(Rgb(122, 98, 70), Rgb(108, 86, 60))
TrenchPalette.NIGHT = TrenchPalette(Rgb(70, 60, 50), Rgb(60, 52, 44))
