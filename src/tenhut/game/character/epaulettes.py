from __future__ import annotations

from typing import Final

from pygame import Rect

from ..painting import Palette
from .painter import Painter


class Epaulettes:
    """Golden shoulder boards with a fringe."""

    COLUMNS: Final = (13, 47)
    BOARD_WIDTH: Final = 12
    BOARD = Rect(0, 39, 12, 4)
    SHINE = Rect(0, 39, 12, 1)
    FRINGE_ROW: Final = 43
    FRINGE_SPACING: Final = 2

    def paint(self, painter: Painter) -> None:
        for column in self.COLUMNS:
            painter.rect(Palette.GOLD, self.BOARD.move(column, 0))
            painter.rect(Palette.GOLD_LIGHT, self.SHINE.move(column, 0))
            for offset in range(0, self.BOARD_WIDTH, self.FRINGE_SPACING):
                painter.rect(Palette.GOLD_DARK, Rect(column + offset, self.FRINGE_ROW, 1, 3))
                painter.rect(Palette.GOLD, Rect(column + offset + 1, self.FRINGE_ROW, 1, 2))
