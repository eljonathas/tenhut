from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass(frozen=True, slots=True)
class LayoutFrame:
    """The screen areas a layout mode decides: scene, chalkboard, button row and the general's centre line."""

    scene: pygame.Rect
    board: pygame.Rect
    buttons: pygame.Rect
    general_x: int
