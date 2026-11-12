from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Verdict:
    """The judge's decision and the General's speech about it."""

    approved: bool
    groups: list[str] = field(default_factory=list)
    minutes: int = 0
    speech: str = ""
    error: str = ""
