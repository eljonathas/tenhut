from __future__ import annotations

import pygame


class SkyMask:
    """A white-where-the-sky-still-shows mask, so aircraft can fly behind buildings, banners and bunting."""

    WHITE = (255, 255, 255, 255)

    def __init__(self, bare_sky: pygame.Surface, painted: pygame.Surface, rows: int) -> None:
        self._mask = pygame.Surface(painted.get_size(), pygame.SRCALPHA)
        for y in range(min(painted.get_height(), rows)):
            for x in range(painted.get_width()):
                if painted.get_at((x, y)) == bare_sky.get_at((x, y)):
                    self._mask.set_at((x, y), self.WHITE)

    @property
    def surface(self) -> pygame.Surface:
        return self._mask
