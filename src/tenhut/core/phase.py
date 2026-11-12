from __future__ import annotations

from enum import StrEnum


class Phase(StrEnum):
    """Where the session is. The values are what state.json stores, so they must not change."""

    IDLE = ("idle", "phase.idle")
    WORK = ("work", "phase.in_combat")
    SHORT = ("short", "phase.short_break")
    LONG = ("long", "phase.long_break")
    VICTORY = ("victory", "phase.victory")

    label_key: str

    def __new__(cls, value: str, label_key: str) -> Phase:
        member = str.__new__(cls, value)
        member._value_ = value
        member.label_key = label_key
        return member

    @property
    def is_break(self) -> bool:
        return self in (Phase.SHORT, Phase.LONG)

    @property
    def in_mission(self) -> bool:
        return self is Phase.WORK or self.is_break
