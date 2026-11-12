from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import pygame


@dataclass(frozen=True, slots=True)
class ClickTarget:
    """A clickable area of the board and what a click on it does."""

    rect: pygame.Rect
    action: Callable[[], None]
