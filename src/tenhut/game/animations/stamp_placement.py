from __future__ import annotations

from dataclasses import dataclass

from tenhut.game.geometry import Point


@dataclass(frozen=True, slots=True)
class StampPlacement:
    """The screen width the stamp must fit in and the point it lands around."""

    screen_width: int
    center: Point
