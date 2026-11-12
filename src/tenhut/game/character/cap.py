from __future__ import annotations

import math
from typing import Final

from pygame import Rect

from ..geometry import Point
from ..painting import Palette
from .character_palette import CharacterPalette
from .painter import Painter


class Cap:
    """The officer's cap: crown, band, golden star badge with laurels, and a visor that turns with his head."""

    CROWN = Rect(15, 2, 42, 15)
    CROWN_HIGHLIGHT = Rect(17, 2, 36, 8)
    CROWN_RIM = Rect(18, 7, 36, 3)
    CROWN_SHADOW = Rect(15, 9, 42, 2)
    BAND = Rect(22, 12, 28, 6)
    BAND_TOP = Rect(22, 12, 28, 1)
    BAND_BOTTOM = Rect(22, 17, 28, 1)

    BADGE_CENTER = Point(36, 9)
    STAR_POINTS: Final = 5
    STAR_OUTER_RADIUS: Final = 5
    STAR_INNER_RADIUS: Final = 2
    LAUREL_LENGTH: Final = 3
    LEFT_LAUREL_START = Point(28, 12)
    RIGHT_LAUREL_START = Point(44, 12)

    VISOR = Rect(21, 16, 30, 6)
    VISOR_SHINE = Rect(24, 17, 24, 1)
    VISOR_STUDS_ROW: Final = 19
    VISOR_STUDS_COLUMNS: Final = range(25, 48, 3)

    def paint(self, painter: Painter, turn: int) -> None:
        self._paint_crown(painter)
        self._paint_band(painter)
        self._paint_badge(painter, turn)
        self._paint_visor(painter, turn)

    def _paint_crown(self, painter: Painter) -> None:
        painter.ellipse(CharacterPalette.CAP, self.CROWN)
        painter.ellipse(CharacterPalette.CAP_LIGHT, self.CROWN_HIGHLIGHT)
        painter.rect(CharacterPalette.CAP, self.CROWN_RIM)
        painter.rect(CharacterPalette.CAP_DARK, self.CROWN_SHADOW)

    def _paint_band(self, painter: Painter) -> None:
        painter.rect(CharacterPalette.CAP_DARK, self.BAND)
        painter.rect(Palette.GOLD, self.BAND_TOP)
        painter.rect(Palette.GOLD_DARK, self.BAND_BOTTOM)

    def _paint_badge(self, painter: Painter, turn: int) -> None:
        center = self.BADGE_CENTER.moved(turn)
        painter.polygon(Palette.GOLD, self._star_points(center))
        painter.pixel(Palette.GOLD_LIGHT, center.moved(0, -1))
        painter.pixel(Palette.GOLD_LIGHT, center.moved(-1, 0))
        for step in range(self.LAUREL_LENGTH):
            painter.pixel(Palette.GOLD_DARK, self.LEFT_LAUREL_START.moved(step + turn, -step))
            painter.pixel(Palette.GOLD_DARK, self.RIGHT_LAUREL_START.moved(-step + turn, -step))

    def _star_points(self, center: Point) -> list[Point]:
        """Alternating outer and inner vertices, starting straight up."""
        vertices = []
        for index in range(2 * self.STAR_POINTS):
            angle = -math.pi / 2 + index * math.pi / self.STAR_POINTS
            radius = self.STAR_OUTER_RADIUS if index % 2 == 0 else self.STAR_INNER_RADIUS
            vertices.append(Point(center.x + radius * math.cos(angle), center.y + radius * math.sin(angle)))
        return vertices

    def _paint_visor(self, painter: Painter, turn: int) -> None:
        painter.ellipse(CharacterPalette.BLACK, self.VISOR.move(turn, 0))
        painter.rect(CharacterPalette.VISOR_HIGHLIGHT, self.VISOR_SHINE.move(turn, 0))
        for column in self.VISOR_STUDS_COLUMNS:
            painter.pixel(Palette.GOLD, Point(column + turn, self.VISOR_STUDS_ROW))
