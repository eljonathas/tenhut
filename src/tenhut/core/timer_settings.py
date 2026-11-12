from __future__ import annotations

from dataclasses import dataclass

from .number_rule import NumberRule


@dataclass(frozen=True, slots=True)
class TimerSettings:
    """Lengths of the work and break blocks."""

    work_minutes: int = 25
    short_break_minutes: int = 5
    long_break_minutes: int = 15
    cycles_before_long_break: int = 4

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> TimerSettings:
        default = cls()
        return cls(
            NumberRule(default.work_minutes, 1, 600).integer(data.get("work_minutes")),
            NumberRule(default.short_break_minutes, 1, 240).integer(data.get("short_break_minutes")),
            NumberRule(default.long_break_minutes, 1, 480).integer(data.get("long_break_minutes")),
            NumberRule(default.cycles_before_long_break, 1, 24).integer(data.get("cycles_before_long_break")),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "work_minutes": self.work_minutes,
            "short_break_minutes": self.short_break_minutes,
            "long_break_minutes": self.long_break_minutes,
            "cycles_before_long_break": self.cycles_before_long_break,
        }
