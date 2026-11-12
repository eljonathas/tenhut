from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass(frozen=True, slots=True)
class TitleCardPlacement:
    """The scene the card hangs from, and the part of the screen it is centred in."""

    scene: pygame.Rect
    region: pygame.Rect
