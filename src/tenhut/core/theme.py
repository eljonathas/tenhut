from __future__ import annotations

import math
from enum import Enum

from .phase import Phase


class Theme(Enum):
    """The four campaign stages, in order of progress."""

    OFFICE = ("office", "theme.office.title")
    FIELD = ("field", "theme.field.title")
    TRENCH = ("trench", "theme.trench.title")
    PARADE = ("parade", "theme.parade.title")

    title_key: str

    def __new__(cls, value: str, title_key: str) -> Theme:
        member = object.__new__(cls)
        member._value_ = value
        member.title_key = title_key
        return member

    @property
    def stage_number(self) -> int:
        return list(Theme).index(self) + 1

    @classmethod
    def for_progress(cls, tasks_done: int, tasks_total: int, phase: Phase, in_mission: bool) -> Theme:
        """The parade after victory, the office outside a mission, else one stage per third of the tasks done."""
        if phase is Phase.VICTORY:
            return cls.PARADE
        if not in_mission or tasks_total <= 0:
            return cls.OFFICE
        stages = list(cls)
        return stages[min(len(stages) - 1, math.ceil(tasks_done / tasks_total * 3))]
