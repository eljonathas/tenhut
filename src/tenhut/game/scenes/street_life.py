from __future__ import annotations

from dataclasses import dataclass

from .banner import Banner
from .crowd import Crowd


@dataclass(frozen=True, slots=True)
class StreetLife:
    """The animated side of the avenue: the crowd on the pavement and the banners on the facades."""

    crowd: Crowd
    banners: tuple[Banner, ...]
