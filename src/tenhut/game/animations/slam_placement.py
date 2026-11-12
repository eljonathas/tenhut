from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SlamPlacement:
    """Where the slam happens on the composed scene surface (logical pixels)."""

    desk_top: int
    world_scale: int
    character_scale: int
    center_x: int
