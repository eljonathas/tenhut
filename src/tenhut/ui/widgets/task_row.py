from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass(frozen=True, slots=True)
class TaskRow:
    """Where one task was drawn last, so a click can be traced back to it."""

    rect: pygame.Rect
    index: int
