from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScreenRect:
    """A rectangle in screen pixels."""

    left: int
    top: int
    right: int
    bottom: int
