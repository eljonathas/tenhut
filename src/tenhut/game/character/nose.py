from __future__ import annotations

from typing import Final

from pygame import Rect

from ..geometry import Point
from .painter import Painter
from .skin_tone import SkinTone


class Nose:
    """The nose, from the front and (when he turns his head far enough) in profile."""

    PROFILE_FROM: Final = 1

    BRIDGE = Rect(35, 28, 3, 5)
    BRIDGE_SHADE = Rect(37, 29, 1, 4)
    NOSTRIL = Point(34, 32)
    PROFILE_COLUMN_RIGHT: Final = 38
    PROFILE_COLUMN_LEFT: Final = 33

    def paint_front(self, painter: Painter, skin: SkinTone) -> None:
        painter.rect(skin.highlight, self.BRIDGE)
        painter.rect(skin.shade, self.BRIDGE_SHADE)
        painter.pixel(skin.shade, self.NOSTRIL)

    def paint_profile(self, painter: Painter, turn: int, skin: SkinTone) -> None:
        if abs(turn) <= self.PROFILE_FROM:
            return
        facing_right = turn > 0
        column = self.PROFILE_COLUMN_RIGHT if facing_right else self.PROFILE_COLUMN_LEFT
        painter.rect(skin.base, Rect(column, 29, 2, 4))
        painter.pixel(skin.shade, Point(column + (1 if facing_right else 0), 32))
