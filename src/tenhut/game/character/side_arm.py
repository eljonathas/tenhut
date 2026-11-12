from __future__ import annotations

from pygame import Rect

from ..painting import Palette
from .painter import Painter


class SideArm:
    """An arm hanging straight down along the body, with its glove."""

    LEFT_COLUMN = 13
    RIGHT_COLUMN = 52
    WIDTH = 7
    SLEEVE_TOP = 43
    SLEEVE_HEIGHT = 23
    CUFF_ROW = 63
    GLOVE_ROW = 66

    def paint(self, painter: Painter, *, left: bool) -> None:
        column = self.LEFT_COLUMN if left else self.RIGHT_COLUMN
        painter.outlined_rect(Palette.OLIVE, Rect(column, self.SLEEVE_TOP, self.WIDTH, self.SLEEVE_HEIGHT))
        shade_column = column if left else column + 5
        painter.rect(Palette.OLIVE_DARK, Rect(shade_column, 45, 2, 20))
        painter.rect(Palette.OLIVE_DARK, Rect(column, self.CUFF_ROW, self.WIDTH, 2))
        painter.rect(Palette.GOLD_DARK, Rect(column, self.CUFF_ROW + 1, self.WIDTH, 1))
        painter.rect(Palette.GLOVE, Rect(column + 1, self.GLOVE_ROW, 5, 4))
        painter.rect(Palette.GLOVE_SHADE, Rect(column + 1, self.GLOVE_ROW + 3, 5, 1))
