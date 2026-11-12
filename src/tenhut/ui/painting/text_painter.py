from __future__ import annotations

import pygame

from tenhut.game.geometry import Point

from .text_style import TextStyle


class TextPainter:
    """Draws unantialiased text on a surface."""

    def __init__(self, surface: pygame.Surface) -> None:
        self._surface = surface

    def draw(self, text: str, position: Point, style: TextStyle) -> pygame.Rect:
        """Draws ``text`` anchored at ``position`` and returns the rectangle it covers."""
        image = style.font.render(text, False, style.color)
        area = image.get_rect()
        setattr(area, style.align.value, position)
        self._surface.blit(image, area)
        return area
