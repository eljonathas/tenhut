from __future__ import annotations

from dataclasses import dataclass

from tenhut.game.geometry import Point


@dataclass(frozen=True, slots=True)
class TaskArea:
    """Where the task list is drawn: its top-left corner, its width and how many rows fit."""

    origin: Point
    width: int
    rows: int
