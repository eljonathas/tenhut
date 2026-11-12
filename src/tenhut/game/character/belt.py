from __future__ import annotations

from pygame import Rect

from ..painting import Palette
from .character_palette import CharacterPalette
from .painter import Painter


class Belt:
    """The leather belt with its golden buckle, which slides with the body turn."""

    STRAP = Rect(19, 63, 34, 4)
    STRAP_EDGE = Rect(19, 66, 34, 1)
    BUCKLE = Rect(33, 63, 6, 4)
    BUCKLE_SLOT = Rect(35, 64, 2, 2)

    def paint(self, painter: Painter, buckle_shift: int) -> None:
        painter.rect(CharacterPalette.BROWN, self.STRAP)
        painter.rect(Palette.BROWN_DARK, self.STRAP_EDGE)
        painter.rect(Palette.GOLD, self.BUCKLE.move(buckle_shift, 0))
        painter.rect(Palette.BROWN_DARK, self.BUCKLE_SLOT.move(buckle_shift, 0))
