from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DepthPoint:
    """A spot on the ground at some depth: where it lands on the canvas and how big things look there."""

    x: float
    y: float
    scale: float
