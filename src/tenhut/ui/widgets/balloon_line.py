from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BalloonLine:
    """One speech waiting for or showing in the balloon, and how long it stays after being typed."""

    message: str
    hold: float
