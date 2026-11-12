from __future__ import annotations

from typing import Final

from ..geometry import Point


class Anatomy:
    """Size of the sprite and the joints that several poses share."""

    WIDTH: Final = 72
    HEIGHT: Final = 96
    OUTLINE_MARGIN: Final = 1
    CANVAS_SIZE: Final = (WIDTH + 2 * OUTLINE_MARGIN, HEIGHT + 2 * OUTLINE_MARGIN)
    LEFT_SHOULDER: Final = Point(16, 46)
    RIGHT_SHOULDER: Final = Point(56, 46)
    FACE_CENTER_COLUMN: Final = 36
