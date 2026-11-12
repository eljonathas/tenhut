from __future__ import annotations

from dataclasses import dataclass, field

from tenhut.core import Task

from ..geometry import Point


@dataclass(frozen=True, slots=True)
class DeskState:
    """The per-frame state of the foreground: mission tasks, desk tremor and how high loose objects hop."""

    tasks: tuple[Task, ...] = ()
    shake: Point = field(default_factory=lambda: Point(0, 0))
    hop: int = 0
