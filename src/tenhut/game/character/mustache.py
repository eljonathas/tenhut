from __future__ import annotations

from pygame import Rect

from ..geometry import Point
from .character_palette import CharacterPalette
from .painter import Painter


class Mustache:
    """The general's thick grey moustache."""

    BULK = (Rect(28, 33, 16, 3), Rect(30, 32, 12, 1), Rect(26, 34, 2, 2), Rect(44, 34, 2, 2))
    TIPS = (Point(25, 33), Point(46, 33))
    TIP_SHADES = (Point(25, 32), Point(46, 32))
    UNDERSIDE = Rect(28, 35, 16, 1)
    PARTING = (Point(36, 33), Point(35, 34))

    def paint(self, painter: Painter) -> None:
        for area in self.BULK:
            painter.rect(CharacterPalette.HAIR, area)
        for tip in self.TIPS:
            painter.pixel(CharacterPalette.HAIR, tip)
        for shade in self.TIP_SHADES:
            painter.pixel(CharacterPalette.HAIR_DARK, shade)
        painter.rect(CharacterPalette.HAIR_DARK, self.UNDERSIDE)
        for point in self.PARTING:
            painter.pixel(CharacterPalette.HAIR_DARK, point)
