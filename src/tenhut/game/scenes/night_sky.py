from __future__ import annotations

import pygame

from tenhut.core import Phase, Theme

from ..painting import Canvas, Rgb
from .sky import Sky
from .sky_colors import SkyColors
from .sky_palette import SkyPalette
from .viewport import Viewport


class NightSky(Sky):
    """Idle: a crescent moon and the stars."""

    MOON_COLOR = Rgb(240, 240, 220)
    MOON_RADIUS = 8
    MOON_RIGHT_MARGIN = 40
    MOON_TOP = 20
    BITE_SHIFT = 3
    BITE_RADIUS = 7
    STAR_DEPTH = 0.8
    WINDOW_STARS = 12
    WINDOW_STAR_DEPTH = 0.6
    WINDOW_MOON_RADIUS = 3
    WINDOW_MOON_RIGHT_MARGIN = 8
    WINDOW_MOON_TOP = 6

    @classmethod
    def colors_for(cls, theme: Theme, phase: Phase) -> SkyColors:
        return SkyPalette.NIGHT

    def paint_body(self, canvas: Canvas, viewport: Viewport, dimmed: bool = False) -> None:
        center = (viewport.width - self.MOON_RIGHT_MARGIN, self.MOON_TOP)
        canvas.circle(self.MOON_COLOR, center, self.MOON_RADIUS)
        bite = (center[0] + self.BITE_SHIFT, center[1] - self.BITE_SHIFT)
        canvas.circle(self._colors.top, bite, self.BITE_RADIUS)
        sky_area = pygame.Rect(0, 0, viewport.width, viewport.horizon_y)
        self._starfield.paint(canvas, sky_area, self.STAR_DEPTH)

    def paint_window_body(self, canvas: Canvas, view: pygame.Rect) -> None:
        self._starfield.paint(canvas, view, self.WINDOW_STAR_DEPTH, limit=self.WINDOW_STARS)
        center = (view.x + view.width - self.WINDOW_MOON_RIGHT_MARGIN, view.y + self.WINDOW_MOON_TOP)
        canvas.circle(self.MOON_COLOR, center, self.WINDOW_MOON_RADIUS)
