from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass(frozen=True, slots=True)
class RowFrame:
    """Where one settings row sits on the board and how tall its controls are."""

    area: pygame.Rect
    top: int
    control_height: int
