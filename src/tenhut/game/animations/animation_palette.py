from __future__ import annotations

from typing import Final

from tenhut.game.painting import Rgb


class AnimationPalette:
    """Colours used only by the animations; the shared ones live in ``Palette``."""

    WOOD: Final = Rgb(128, 82, 46)
    WOOD_LIGHT: Final = Rgb(170, 116, 68)
    WOOD_DARK: Final = Rgb(86, 52, 28)
    YELLOW: Final = Rgb(250, 214, 90)
    CREAM: Final = Rgb(255, 240, 200)
    IMPACT_TEXT: Final = Rgb(255, 226, 90)
    IMPACT_STREAK: Final = Rgb(255, 240, 180)
    SLAM_TEXT: Final = Rgb(240, 70, 60)
    DUST: Final = Rgb(250, 240, 200)
    FIST_FOLD: Final = Rgb(196, 196, 196)
