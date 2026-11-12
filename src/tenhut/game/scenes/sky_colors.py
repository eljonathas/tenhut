from __future__ import annotations

from typing import NamedTuple

from ..painting import Rgb


class SkyColors(NamedTuple):
    """The two ends of a sky gradient."""

    top: Rgb
    horizon: Rgb
