from __future__ import annotations

from typing import Final

from pygame import Rect

from ..geometry import Point
from ..painting import Palette, Rgb
from .character_palette import CharacterPalette
from .painter import Painter


class Medals:
    """The ribbon grid and the big star on his left breast (the right of the picture), and the pin on the other side."""

    RIBBON_COLORS: Final[tuple[Rgb, ...]] = (
        Palette.RED,
        Palette.GOLD,
        CharacterPalette.BLUE,
        CharacterPalette.GREEN,
        Palette.WHITE,
        Palette.RED,
        CharacterPalette.BLUE,
        Palette.GOLD,
        CharacterPalette.GREEN,
    )
    GRID_COLUMNS: Final = 3
    GRID_ORIGIN = Point(40, 45)
    RIBBON_SIZE = (3, 2)
    COLUMN_SPACING: Final = 3
    ROW_SPACING: Final = 2

    STAR_RIBBON = Rect(43, 51, 1, 2)
    STAR_MEDAL = Rect(41, 52, 5, 5)
    STAR_GLINT = Point(43, 54)

    PIN_RIBBON = Rect(24, 46, 4, 2)
    PIN_MEDAL = Rect(24, 48, 4, 4)

    def paint(self, painter: Painter) -> None:
        self._paint_ribbons(painter)
        painter.rect(Palette.RED, self.STAR_RIBBON)
        painter.ellipse(Palette.GOLD, self.STAR_MEDAL)
        painter.pixel(Palette.GOLD_LIGHT, self.STAR_GLINT)
        painter.rect(CharacterPalette.BLUE, self.PIN_RIBBON)
        painter.ellipse(Palette.GOLD_DARK, self.PIN_MEDAL)

    def _paint_ribbons(self, painter: Painter) -> None:
        for index, color in enumerate(self.RIBBON_COLORS):
            row, column = divmod(index, self.GRID_COLUMNS)
            origin = self.GRID_ORIGIN.moved(column * self.COLUMN_SPACING, row * self.ROW_SPACING)
            painter.rect(color, Rect(origin, self.RIBBON_SIZE))
            painter.pixel(Palette.OLIVE_DARK, origin.moved(2, 1))
