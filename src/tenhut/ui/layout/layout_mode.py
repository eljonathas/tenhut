from __future__ import annotations

from enum import Enum


class LayoutMode(Enum):
    """WIDE: general left, board right. TALL: general on top, board below. MINI: a compact widget."""

    WIDE = "wide"
    TALL = "tall"
    MINI = "mini"
