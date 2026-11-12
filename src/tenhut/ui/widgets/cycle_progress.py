from __future__ import annotations

from dataclasses import dataclass

from tenhut.core import Phase


@dataclass(frozen=True, slots=True)
class CycleProgress:
    """How many pomodoros of the cycle that ends in a long break are done."""

    phase: Phase
    cycles: int
    per_cycle: int

    @property
    def finished(self) -> int:
        if self.phase is Phase.LONG:
            return self.per_cycle
        if self.phase in (Phase.WORK, Phase.SHORT):
            return self.cycles % self.per_cycle
        return 0
