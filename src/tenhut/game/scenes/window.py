from __future__ import annotations

from typing import ClassVar

import pygame

from ..painting import Canvas, Rgb
from .mountain_range import MountainRange
from .scene_canvas import SceneCanvas
from .sky import Sky


class Window:
    """A wooden window onto the sky, with distant hills."""

    FRAME: ClassVar[Rgb] = Rgb(112, 76, 44)
    SILL: ClassVar[Rgb] = Rgb(92, 60, 34)
    SKY_BANDS: ClassVar[int] = 5
    HILL_SHADE: ClassVar[float] = 0.62
    HILL_AMPLITUDE: ClassVar[int] = 6
    HILL_BASE_INSET: ClassVar[int] = 2
    FRAME_THICKNESS: ClassVar[int] = 2
    SILL_OVERHANG: ClassVar[int] = 4
    SILL_THICKNESS: ClassVar[int] = 3

    def __init__(self, view: pygame.Rect, sky: Sky) -> None:
        self._view = view
        self._sky = sky

    def draw(self, canvas: SceneCanvas) -> None:
        view = self._view
        self._sky.paint_gradient(canvas, view, self.SKY_BANDS)
        self._sky.paint_window_body(canvas, view)
        hills = MountainRange(self._sky.horizon_color.shaded(self.HILL_SHADE), self.HILL_AMPLITUDE)
        hills.paint(canvas.window(view), view.width, view.height - self.HILL_BASE_INSET)
        self._draw_frame(canvas)

    def _draw_frame(self, canvas: Canvas) -> None:
        view = self._view
        margin = self.FRAME_THICKNESS
        canvas.rect(
            self.FRAME,
            (view.x - margin, view.y - margin, view.width + 2 * margin, view.height + 2 * margin),
            border=margin,
        )
        canvas.line(self.FRAME, (view.centerx, view.y), (view.centerx, view.y + view.height))
        canvas.line(self.FRAME, (view.x, view.y + view.height // 2), (view.x + view.width, view.y + view.height // 2))
        sill = (
            view.x - self.SILL_OVERHANG,
            view.y + view.height + margin,
            view.width + 2 * self.SILL_OVERHANG,
            self.SILL_THICKNESS,
        )
        canvas.rect(self.SILL, sill)
