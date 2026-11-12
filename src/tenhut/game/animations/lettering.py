from __future__ import annotations

import pygame
from pygame.typing import ColorLike
from pygame.typing import Point as PygamePoint


class Lettering:
    """Draws and measures text in one pixel font."""

    ELLIPSIS = "…"

    def __init__(self, font: pygame.font.Font) -> None:
        self._font = font

    def width(self, text: str) -> int:
        return self._font.size(text)[0]

    def fitted(self, text: str, max_width: int) -> str:
        """The text, cut and closed with an ellipsis when it does not fit in ``max_width``."""
        if self.width(text) <= max_width:
            return text
        while text and self.width(text + self.ELLIPSIS) > max_width:
            text = text[:-1]
        return text + self.ELLIPSIS

    def draw_centered(self, surface: pygame.Surface, text: str, center: PygamePoint, color: ColorLike) -> None:
        image = self._font.render(text, False, color)
        surface.blit(image, image.get_rect(center=center))
