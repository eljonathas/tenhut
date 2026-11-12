from __future__ import annotations

from typing import Final

from .rgb import Rgb


class Palette:
    """Colours shared by the character, the scenes and the animations."""

    OUTLINE: Final = Rgb(26, 22, 32)
    WHITE: Final = Rgb(250, 250, 246)
    OLIVE: Final = Rgb(88, 112, 60)
    OLIVE_DARK: Final = Rgb(62, 82, 42)
    OLIVE_LIGHT: Final = Rgb(114, 140, 76)
    GOLD: Final = Rgb(240, 198, 70)
    GOLD_DARK: Final = Rgb(180, 134, 38)
    GOLD_LIGHT: Final = Rgb(255, 236, 150)
    GLOVE: Final = Rgb(244, 244, 238)
    GLOVE_SHADE: Final = Rgb(196, 196, 196)
    RED: Final = Rgb(200, 52, 52)
    BROWN_DARK: Final = Rgb(78, 48, 26)
