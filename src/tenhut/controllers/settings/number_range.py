from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NumberRange:
    """How a number option moves: by ``step`` at a time, between ``low`` and ``high``."""

    step: float
    low: float
    high: float
