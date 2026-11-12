from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChatterRule:
    """What the general mutters when idle in a phase, and how long he waits between remarks."""

    key: str
    min_seconds: float
    max_seconds: float
