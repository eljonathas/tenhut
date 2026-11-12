from __future__ import annotations

from dataclasses import dataclass, field

from ...core import Phase, Task


@dataclass(frozen=True, slots=True)
class JudgeContext:
    """What the judge may know about the session."""

    tasks: tuple[Task, ...]
    phase: Phase
    remaining: str
    cycles: int
    groups: tuple[str, ...]
    history: tuple[str, ...] = field(default_factory=tuple)
