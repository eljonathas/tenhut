from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Rank:
    """A military rank reached at `min_xp`; `name_key` is its translation key."""

    min_xp: int
    name_key: str
