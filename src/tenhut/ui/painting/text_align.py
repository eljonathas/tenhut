from __future__ import annotations

from enum import Enum


class TextAlign(Enum):
    """Which corner of the rendered text sits on the given position (the value names the pygame rect attribute)."""

    LEFT = "topleft"
    CENTER = "center"
    RIGHT = "topright"
