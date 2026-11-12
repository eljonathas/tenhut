from __future__ import annotations

from typing import NamedTuple


class Bounce(NamedTuple):
    """How a spectator hops: radians of phase per second and hop height in pixels at full size."""

    rate: float
    height: float
