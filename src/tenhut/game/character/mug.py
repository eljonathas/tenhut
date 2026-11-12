from __future__ import annotations

from typing import Final

from pygame import Rect

from ..geometry import Point
from ..painting import Palette
from .character_palette import CharacterPalette
from .painter import Painter


class Mug:
    """A red coffee mug with a few steam pixels that rise in turns."""

    STEAM_PUFFS: Final = 3
    STEAM_FRAMES_PER_SECOND: Final = 4

    def paint(self, painter: Painter, origin: Point, elapsed: float) -> None:
        x, y = origin
        painter.rect(Palette.OUTLINE, Rect(x - 1, y - 1, 12, 11))
        painter.rect(CharacterPalette.MUG, Rect(x, y, 8, 9))
        painter.rect(Palette.WHITE, Rect(x, y, 8, 1))
        painter.rect(Palette.BROWN_DARK, Rect(x + 1, y + 1, 6, 1))
        for handle in (Rect(x + 8, y + 2, 2, 1), Rect(x + 9, y + 2, 1, 4), Rect(x + 8, y + 5, 2, 1)):
            painter.rect(CharacterPalette.MUG, handle)
        painter.rect(Palette.WHITE, Rect(x + 2, y + 4, 4, 2))
        painter.rect(Palette.GLOVE, Rect(x + 7, y + 6, 4, 4))
        self._paint_steam(painter, origin, elapsed)

    def _paint_steam(self, painter: Painter, origin: Point, elapsed: float) -> None:
        phase = int(elapsed * self.STEAM_FRAMES_PER_SECOND) % self.STEAM_PUFFS
        for puff in range(self.STEAM_PUFFS):
            sway = ((puff + phase) % 2) * 2
            painter.pixel(CharacterPalette.STEAM, Point(origin.x + 2 + sway, origin.y - 2 - puff * 2))
