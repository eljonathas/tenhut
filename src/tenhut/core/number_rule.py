from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NumberRule:
    """Default and allowed range of a numeric setting; untrusted values are coerced to it."""

    default: float
    low: float
    high: float

    @staticmethod
    def _is_number(value: object) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

    def integer(self, value: object) -> int:
        if not self._is_number(value):
            return int(self.default)
        return int(max(self.low, min(self.high, value)))

    def real(self, value: object) -> float:
        """Whole numbers come back as int so the file keeps reading `6`, not `6.0`."""
        if not self._is_number(value):
            return self.default
        clamped = max(self.low, min(self.high, value))
        return int(clamped) if float(clamped).is_integer() else float(clamped)
