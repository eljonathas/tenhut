from __future__ import annotations

from typing import Final

from pygame import Rect

from .character_palette import CharacterPalette
from .painter import Painter


class Boots:
    """Both boots and the floor line under them; the toes point sideways when he turns."""

    TURNED_FROM: Final = 1

    LEFT_BOOT = Rect(24, 85, 12, 6)
    RIGHT_BOOT = Rect(36, 85, 12, 6)
    LEFT_SHINE = Rect(25, 86, 4, 1)
    RIGHT_SHINE = Rect(38, 86, 4, 1)
    LEFT_FLOOR = Rect(23, 90, 13, 1)
    RIGHT_FLOOR = Rect(36, 90, 13, 1)

    SIDE_HEELS: Final = (25, 37)
    SIDE_BOOT = Rect(0, 85, 10, 6)
    SIDE_TOE_SIZE = (5, 4)
    SIDE_SHINE = Rect(2, 86, 4, 1)
    SIDE_FLOOR_WIDTH: Final = 14

    def paint(self, painter: Painter, turn: int) -> None:
        """``painter`` must be grounded: boots do not bob with the breathing."""
        direction = (turn > self.TURNED_FROM) - (turn < -self.TURNED_FROM)
        if direction:
            self._paint_sideways(painter, direction)
        else:
            self._paint_frontal(painter)

    def _paint_frontal(self, painter: Painter) -> None:
        for boot in (self.LEFT_BOOT, self.RIGHT_BOOT):
            painter.rect(CharacterPalette.BOOT, boot)
        for shine in (self.LEFT_SHINE, self.RIGHT_SHINE):
            painter.rect(CharacterPalette.BOOT_HIGHLIGHT, shine)
        for floor in (self.LEFT_FLOOR, self.RIGHT_FLOOR):
            painter.rect(CharacterPalette.BLACK, floor)

    def _paint_sideways(self, painter: Painter, direction: int) -> None:
        for heel in self.SIDE_HEELS:
            painter.rect(CharacterPalette.BOOT, self.SIDE_BOOT.move(heel + direction, 0))
            toe_column = heel + (8 if direction > 0 else -3) + direction
            painter.rect(CharacterPalette.BOOT, Rect((toe_column, 87), self.SIDE_TOE_SIZE))
            painter.rect(CharacterPalette.BOOT_HIGHLIGHT, self.SIDE_SHINE.move(heel + direction, 0))
            floor_column = heel - (3 if direction < 0 else 0) + direction
            painter.rect(CharacterPalette.BLACK, Rect(floor_column, 90, self.SIDE_FLOOR_WIDTH, 1))
