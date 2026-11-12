from __future__ import annotations

from abc import ABC, abstractmethod

import pygame

from tenhut.core import Phase, Theme

from ..painting import Canvas, Rgb
from .sky_colors import SkyColors
from .starfield import Starfield
from .viewport import Viewport


class Sky(ABC):
    """The sky of one theme in one phase: its gradient and whatever hangs in it."""

    GRADIENT_BANDS = 10
    SUN_RADIUS = 10
    SUN_CORE_RADIUS = 7
    SUN_COLOR = Rgb(255, 240, 170)
    SUN_CORE_COLOR = Rgb(255, 252, 220)
    DIM_SUN_COLOR = Rgb(230, 200, 160)
    DIM_SUN_CORE_COLOR = Rgb(240, 220, 190)
    WINDOW_SUN_COLOR = Rgb(255, 244, 180)
    WINDOW_SUN_LEFT = 9
    WINDOW_SUN_TOP = 7
    WINDOW_SUN_RADIUS = 4

    def __init__(self, colors: SkyColors, starfield: Starfield) -> None:
        self._colors = colors
        self._starfield = starfield

    @property
    def colors(self) -> SkyColors:
        return self._colors

    @property
    def horizon_color(self) -> Rgb:
        return self._colors.horizon

    def paint_gradient(self, canvas: Canvas, area: pygame.Rect, bands: int = GRADIENT_BANDS) -> None:
        top, bottom = self._colors
        for band in range(bands):
            color = top.mixed_with(bottom, band / max(1, bands - 1))
            canvas.rect(color, (area.x, area.y + band * area.height // bands, area.width, area.height // bands + 2))

    @classmethod
    @abstractmethod
    def colors_for(cls, theme: Theme, phase: Phase) -> SkyColors:
        """The gradient this kind of sky has for the theme."""

    @abstractmethod
    def paint_body(self, canvas: Canvas, viewport: Viewport, dimmed: bool = False) -> None:
        """The sun, or the moon and stars, high over the horizon."""

    def paint_window_body(self, canvas: Canvas, view: pygame.Rect) -> None:
        center = (view.x + self.WINDOW_SUN_LEFT, view.y + self.WINDOW_SUN_TOP)
        canvas.circle(self.WINDOW_SUN_COLOR, center, self.WINDOW_SUN_RADIUS)

    def _paint_sun(self, canvas: Canvas, center: tuple[int, int], dimmed: bool) -> None:
        outer, core = (self.DIM_SUN_COLOR, self.DIM_SUN_CORE_COLOR) if dimmed else (self.SUN_COLOR, self.SUN_CORE_COLOR)
        canvas.circle(outer, center, self.SUN_RADIUS)
        canvas.circle(core, center, self.SUN_CORE_RADIUS)
