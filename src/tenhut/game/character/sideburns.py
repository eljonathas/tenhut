from __future__ import annotations

from typing import Final

from pygame import Rect

from .character_palette import CharacterPalette
from .painter import Painter


class Sideburns:
    """Grey sideburns; seen from the side, the hair at the back of the head shows instead."""

    TURNED_FROM: Final = 2

    FRONT = (Rect(24, 21, 2, 8), Rect(46, 21, 2, 8))
    LEFT_PROFILE = (Rect(24, 20, 5, 10), Rect(24, 29, 3, 3))
    RIGHT_PROFILE = (Rect(43, 20, 5, 10), Rect(45, 29, 3, 3))

    def paint(self, painter: Painter, turn: int) -> None:
        if turn >= self.TURNED_FROM:
            self._paint_profile(painter, self.LEFT_PROFILE)
        elif turn <= -self.TURNED_FROM:
            self._paint_profile(painter, self.RIGHT_PROFILE)
        else:
            for area in self.FRONT:
                painter.rect(CharacterPalette.HAIR, area)

    @staticmethod
    def _paint_profile(painter: Painter, areas: tuple[Rect, Rect]) -> None:
        painter.rect(CharacterPalette.HAIR, areas[0])
        painter.rect(CharacterPalette.HAIR_DARK, areas[1])
