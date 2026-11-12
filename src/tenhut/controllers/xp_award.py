from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class XpAward:
    """Experience earned, and what earned it."""

    points: int
    pomodoro: bool = False
    mission: bool = False
