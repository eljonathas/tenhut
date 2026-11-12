from __future__ import annotations

from typing import Final

from tenhut.core import Theme

from ..painting import Rgb
from .sky_colors import SkyColors


class SkyPalette:
    """The sky gradients: one per theme in daylight, plus the night, sunset and parade-victory skies."""

    NIGHT: Final = SkyColors(Rgb(30, 34, 76), Rgb(96, 86, 136))
    SUNSET: Final = SkyColors(Rgb(236, 128, 96), Rgb(254, 214, 150))
    PARADE_VICTORY: Final = SkyColors(Rgb(40, 50, 110), Rgb(210, 120, 140))
    _DAYLIGHT: Final = {
        Theme.OFFICE: SkyColors(Rgb(96, 156, 222), Rgb(186, 222, 244)),
        Theme.FIELD: SkyColors(Rgb(84, 140, 210), Rgb(176, 214, 240)),
        Theme.TRENCH: SkyColors(Rgb(78, 86, 116), Rgb(176, 150, 132)),
        Theme.PARADE: SkyColors(Rgb(80, 150, 230), Rgb(214, 232, 246)),
    }

    @classmethod
    def daylight(cls, theme: Theme) -> SkyColors:
        return cls._DAYLIGHT[theme]
