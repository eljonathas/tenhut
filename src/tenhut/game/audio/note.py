from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Note:
    """One tone of ``frequency`` Hz held for ``duration`` seconds; a frequency of zero is a rest."""

    frequency: float
    duration: float

    @classmethod
    def rest(cls, duration: float) -> Note:
        return cls(0, duration)

    @property
    def is_rest(self) -> bool:
        return self.frequency <= 0
