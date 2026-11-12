from __future__ import annotations

from typing import Final

from tenhut.game.painting import Rgb


class UiPalette:
    """Colours of the interface: the chalkboard, the wooden frame and the signal colours."""

    INK: Final = Rgb(26, 22, 32)
    PAPER: Final = Rgb(252, 250, 240)
    SHADOW: Final = Rgb(0, 0, 0)
    CHALK: Final = Rgb(236, 240, 226)
    CHALK_DIM: Final = Rgb(160, 178, 158)
    BOARD: Final = Rgb(36, 64, 48)
    BOARD_DARK: Final = Rgb(26, 48, 36)
    WOOD: Final = Rgb(128, 82, 46)
    WOOD_DARK: Final = Rgb(86, 52, 28)
    WOOD_LIGHT: Final = Rgb(170, 116, 68)
    YELLOW: Final = Rgb(250, 214, 90)
    RED: Final = Rgb(214, 64, 56)
    GREEN: Final = Rgb(84, 170, 84)
    GRAY: Final = Rgb(110, 110, 110)
    SALMON: Final = Rgb(255, 140, 120)
    CORAL: Final = Rgb(255, 150, 130)
    SCARLET: Final = Rgb(255, 120, 100)
    PEACH: Final = Rgb(240, 160, 140)
    MINT: Final = Rgb(140, 230, 140)
    PROGRESS_WORK: Final = Rgb(230, 110, 90)
    PROGRESS_EMPTY: Final = Rgb(60, 90, 70)
    TOMATO: Final = Rgb(220, 60, 50)
    TOMATO_STEM: Final = Rgb(80, 160, 70)
    NAIL: Final = Rgb(210, 200, 180)
    PLATE_TEXT: Final = Rgb(255, 240, 200)
    FIELD_IDLE: Final = Rgb(232, 228, 214)
    FIELD_HINT: Final = Rgb(150, 144, 130)
    DISABLED_FACE: Final = Rgb(150, 150, 150)
    DISABLED_SHADE: Final = Rgb(110, 110, 110)
    DISABLED_TEXT: Final = Rgb(70, 70, 70)
    STEPPER: Final = Rgb(222, 196, 146)
    CALIBRATE: Final = Rgb(92, 140, 214)
    INSTALL: Final = Rgb(214, 150, 70)
    THOUGHT: Final = Rgb(250, 250, 250)
    GROUND: Final = Rgb(66, 48, 34)
    LETTERBOX: Final = Rgb(14, 12, 18)
    VICTORY_STAMP: Final = Rgb(250, 214, 90)
