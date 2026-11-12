from __future__ import annotations

from typing import Final

from ..painting import Rgb


class CharacterPalette:
    """Colours only the general uses; the ones shared with the scenes live in ``Palette``."""

    SKIN: Final = Rgb(238, 190, 142)
    SKIN_SHADE: Final = Rgb(206, 150, 106)
    SKIN_HIGHLIGHT: Final = Rgb(250, 214, 174)
    SKIN_FLUSHED: Final = Rgb(236, 128, 104)
    SKIN_FLUSHED_SHADE: Final = Rgb(200, 92, 76)
    CAP: Final = Rgb(64, 86, 46)
    CAP_DARK: Final = Rgb(40, 56, 30)
    CAP_LIGHT: Final = Rgb(88, 114, 62)
    BLACK: Final = Rgb(30, 26, 34)
    VISOR_HIGHLIGHT: Final = Rgb(90, 86, 100)
    HAIR: Final = Rgb(214, 214, 222)
    HAIR_DARK: Final = Rgb(154, 154, 168)
    BLUE: Final = Rgb(56, 96, 190)
    GREEN: Final = Rgb(56, 160, 80)
    BOOT: Final = Rgb(40, 32, 32)
    BOOT_HIGHLIGHT: Final = Rgb(82, 70, 72)
    BROWN: Final = Rgb(112, 72, 40)
    MUG: Final = Rgb(226, 70, 60)
    MOUTH: Final = Rgb(110, 30, 40)
    CHEEK: Final = Rgb(242, 150, 140)
    PUPIL_GLINT: Final = Rgb(80, 80, 110)
    STEAM: Final = Rgb(235, 235, 240)
