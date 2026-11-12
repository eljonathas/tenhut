from __future__ import annotations

from pygame import Rect

from .painter import Painter
from .skin_tone import SkinTone


class Ears:
    """Both ears; the one on the side he turns away from disappears behind the head."""

    LEFT_EAR = Rect(21, 23, 6, 9)
    LEFT_SHADOW = Rect(23, 26, 1, 3)
    RIGHT_EAR = Rect(45, 23, 6, 9)
    RIGHT_SHADOW = Rect(48, 26, 1, 3)
    HIDDEN_BEYOND = 1

    def paint(self, painter: Painter, turn: int, skin: SkinTone) -> None:
        if turn >= -self.HIDDEN_BEYOND:
            painter.ellipse(skin.base, self.LEFT_EAR)
            painter.rect(skin.shade, self.LEFT_SHADOW)
        if turn <= self.HIDDEN_BEYOND:
            painter.ellipse(skin.base, self.RIGHT_EAR)
            painter.rect(skin.shade, self.RIGHT_SHADOW)
