from __future__ import annotations

from enum import IntEnum


class Side(IntEnum):
    """Which side of the vanishing line; the value is the sign of the horizontal offset."""

    LEFT = -1
    RIGHT = 1
