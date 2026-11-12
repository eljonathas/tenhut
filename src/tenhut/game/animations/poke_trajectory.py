from __future__ import annotations

from dataclasses import dataclass

from tenhut.game.geometry import Point


@dataclass(frozen=True, slots=True)
class PokeTrajectory:
    """Where the poking arm starts, where the glove ends up and how big it looks at each end."""

    shoulder: Point
    target: Point
    small_size: float
    big_size: float
    sleeve_half_width: float
