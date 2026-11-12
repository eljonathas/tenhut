from __future__ import annotations

from typing import Final

import pygame

from ..painting import Palette

TRANSPARENT: Final = (0, 0, 0, 0)
NEIGHBOURS: Final = ((-1, 0), (1, 0), (0, -1), (0, 1))


class OutlineRenderer:
    """Wraps a sprite in a one pixel dark outline: its silhouette, shifted in the four directions, under it."""

    def outline(self, body: pygame.Surface) -> pygame.Surface:
        silhouette = pygame.mask.from_surface(body).to_surface(setcolor=Palette.OUTLINE, unsetcolor=TRANSPARENT)
        outlined = pygame.Surface(body.get_size(), pygame.SRCALPHA)
        for neighbour in NEIGHBOURS:
            outlined.blit(silhouette, neighbour)
        outlined.blit(body, (0, 0))
        return outlined
