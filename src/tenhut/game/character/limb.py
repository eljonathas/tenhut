from __future__ import annotations

from dataclasses import dataclass

from ..geometry import Point


@dataclass(frozen=True, slots=True)
class Limb:
    """A thick rounded segment between two joints."""

    start: Point
    end: Point
    thickness: int = 7
