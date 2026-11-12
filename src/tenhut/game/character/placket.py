from __future__ import annotations

from pygame import Rect

from ..geometry import Point
from ..painting import Palette
from .character_palette import CharacterPalette
from .painter import Painter


class Placket:
    """The front of the jacket: lapels, neck, collar tabs and buttons. Drawn already shifted by the body turn."""

    LEFT_LAPEL = (Point(30, 42), Point(36, 52), Point(36, 42))
    RIGHT_LAPEL = (Point(42, 42), Point(36, 52), Point(36, 42))
    LAPEL_HIGHLIGHT = (Point(30, 43), Point(35, 51))
    NECK = Rect(31, 37, 10, 5)
    COLLAR_TABS = (Rect(29, 40, 4, 4), Rect(39, 40, 4, 4))
    COLLAR_PINS = (Point(30, 41), Point(41, 41))
    BUTTON_ROWS = (53, 58)
    BUTTON_COLUMN = 36

    def paint(self, painter: Painter) -> None:
        self._paint_lapels(painter)
        self._paint_collar(painter)
        self._paint_buttons(painter)

    def _paint_lapels(self, painter: Painter) -> None:
        painter.polygon(Palette.OLIVE_DARK, self.LEFT_LAPEL)
        painter.polygon(Palette.OLIVE_DARK, self.RIGHT_LAPEL)
        painter.line(Palette.OLIVE_LIGHT, *self.LAPEL_HIGHLIGHT)

    def _paint_collar(self, painter: Painter) -> None:
        painter.rect(CharacterPalette.SKIN_SHADE, self.NECK)
        for tab in self.COLLAR_TABS:
            painter.rect(Palette.RED, tab)
        for pin in self.COLLAR_PINS:
            painter.pixel(Palette.GOLD, pin)

    def _paint_buttons(self, painter: Painter) -> None:
        for row in self.BUTTON_ROWS:
            painter.pixel(Palette.GOLD, Point(self.BUTTON_COLUMN, row))
            painter.pixel(Palette.GOLD_DARK, Point(self.BUTTON_COLUMN - 1, row))
