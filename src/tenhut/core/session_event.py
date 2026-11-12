from __future__ import annotations

from enum import StrEnum


class SessionEvent(StrEnum):
    """What `Session.tick` reports."""

    WORK_END = "work_end"
    BREAK_END = "break_end"
    VICTORY = "victory"
