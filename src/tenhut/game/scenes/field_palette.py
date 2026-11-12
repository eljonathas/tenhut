from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ..painting import Rgb


@dataclass(frozen=True, slots=True)
class FieldPalette:
    """Ground colours of the training field, by day or by night."""

    hills: Rgb
    grass: Rgb
    grass_alt: Rgb
    dirt: Rgb

    DAY: ClassVar[FieldPalette]
    NIGHT: ClassVar[FieldPalette]


FieldPalette.DAY = FieldPalette(Rgb(96, 132, 92), Rgb(104, 164, 78), Rgb(92, 150, 68), Rgb(184, 148, 98))
FieldPalette.NIGHT = FieldPalette(Rgb(52, 70, 60), Rgb(54, 86, 60), Rgb(46, 76, 52), Rgb(110, 92, 70))
