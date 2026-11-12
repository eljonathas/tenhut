from __future__ import annotations

from dataclasses import dataclass

from ..random_source import RandomSource


@dataclass(frozen=True, slots=True)
class AmbientFrame:
    """The clock, world size and dice that the shared ambient effects need for one update."""

    elapsed: float
    world_width: int
    world_height: int
    randomness: RandomSource
