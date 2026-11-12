from __future__ import annotations

from tenhut.core import Phase, Theme

from ..painting import Canvas
from .sky import Sky
from .sky_colors import SkyColors
from .sky_palette import SkyPalette
from .viewport import Viewport


class DaySky(Sky):
    """Daylight: the sun up on the left of the soldier's view."""

    SUN_MIN_X = 16
    SUN_MIN_Y = 14
    SUN_LEFT_SHARE = 0.25
    SUN_HEIGHT_DIVISOR = 4

    @classmethod
    def colors_for(cls, theme: Theme, phase: Phase) -> SkyColors:
        if theme is Theme.PARADE and phase is Phase.VICTORY:
            return SkyPalette.PARADE_VICTORY
        return SkyPalette.daylight(theme)

    def paint_body(self, canvas: Canvas, viewport: Viewport, dimmed: bool = False) -> None:
        x = max(self.SUN_MIN_X, viewport.vanishing_x - int(viewport.width * self.SUN_LEFT_SHARE))
        y = max(self.SUN_MIN_Y, viewport.horizon_y // self.SUN_HEIGHT_DIVISOR)
        self._paint_sun(canvas, (x, y), dimmed)
