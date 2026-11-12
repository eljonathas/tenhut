from __future__ import annotations

from typing import Final

from tenhut.core import Phase, Theme

from .day_sky import DaySky
from .night_sky import NightSky
from .sky import Sky
from .starfield import Starfield
from .sunset_sky import SunsetSky


class SkyFactory:
    """Builds the sky for a theme and phase; any phase without a special sky gets daylight."""

    _BY_PHASE: Final[dict[Phase, type[Sky]]] = {
        Phase.IDLE: NightSky,
        Phase.SHORT: SunsetSky,
        Phase.LONG: SunsetSky,
    }

    def __init__(self, starfield: Starfield) -> None:
        self._starfield = starfield

    def create(self, theme: Theme, phase: Phase) -> Sky:
        sky_type = self._BY_PHASE.get(phase, DaySky)
        return sky_type(sky_type.colors_for(theme, phase), self._starfield)
