from __future__ import annotations

import pygame
from pygame.typing import ColorLike
from pygame.typing import Point as PygamePoint

from ..painting import Canvas


class SceneCanvas(Canvas):
    """The shared canvas plus the few extra strokes the scenes need."""

    def fill(self, color: ColorLike) -> None:
        self.surface.fill(color)

    def lower_half_circle(self, color: ColorLike, center: PygamePoint, radius: int) -> None:
        pygame.draw.circle(
            self.surface,
            color,
            center,
            radius,
            0,
            draw_top_right=False,
            draw_top_left=False,
            draw_bottom_left=True,
            draw_bottom_right=True,
        )

    def window(self, area: pygame.Rect) -> SceneCanvas:
        """A canvas on a sub-rectangle of this one, with its own origin."""
        return SceneCanvas(self.surface.subsurface(area))
