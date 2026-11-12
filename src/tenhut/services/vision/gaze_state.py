from __future__ import annotations

from enum import StrEnum


class GazeState(StrEnum):
    """What the head pose means for the focus rules."""

    OK = "ok"
    DOWN = "down"
    SIDE = "side"
    SIDE_ALLOWED = "side_allowed"

    @property
    def is_infraction(self) -> bool:
        return self in (GazeState.DOWN, GazeState.SIDE)
