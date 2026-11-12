from __future__ import annotations

from tenhut.core import Phase, Theme

from ..painting import Canvas
from .sky import Sky
from .sky_colors import SkyColors
from .sky_palette import SkyPalette
from .viewport import Viewport


class SunsetSky(Sky):
    """Break time: the sun sits low next to the horizon."""

    SUN_LEFT_OFFSET = 40
    SUN_ABOVE_HORIZON = 6

    @classmethod
    def colors_for(cls, theme: Theme, phase: Phase) -> SkyColors:
        return SkyPalette.SUNSET

    def paint_body(self, canvas: Canvas, viewport: Viewport, dimmed: bool = False) -> None:
        center = (viewport.vanishing_x - self.SUN_LEFT_OFFSET, viewport.horizon_y - self.SUN_ABOVE_HORIZON)
        self._paint_sun(canvas, center, dimmed)
