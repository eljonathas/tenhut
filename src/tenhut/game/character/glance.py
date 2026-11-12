from __future__ import annotations

from dataclasses import dataclass

from ..geometry import Point


@dataclass(frozen=True, slots=True)
class Glance:
    """Where the eyes go next (each axis from -1 to 1) and whether they narrow."""

    target: Point
    squint: bool
