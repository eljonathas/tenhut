from __future__ import annotations

from pygame import Rect

from .painter import Painter
from .skin_tone import SkinTone


class Skull:
    """The cranium with its square jaw and the shade under the cap and along the right cheek."""

    CRANIUM = Rect(24, 13, 24, 26)
    FACE_MASS = (Rect(25, 26, 22, 12), Rect(27, 37, 18, 3), Rect(29, 40, 14, 1))
    SHADOWS = (Rect(45, 24, 2, 13), Rect(43, 37, 2, 3), Rect(25, 20, 22, 2))

    def paint(self, painter: Painter, skin: SkinTone) -> None:
        painter.ellipse(skin.base, self.CRANIUM)
        for area in self.FACE_MASS:
            painter.rect(skin.base, area)
        for area in self.SHADOWS:
            painter.rect(skin.shade, area)
