from __future__ import annotations

from .number_range import NumberRange
from .row_editor import RowEditor


class NumberEditor(RowEditor):
    """A number that moves by a step within a range."""

    def __init__(self, bounds: NumberRange) -> None:
        self._bounds = bounds

    def adjust(self, current: object, direction: int) -> object:
        bounds = self._bounds
        return max(bounds.low, min(bounds.high, current + bounds.step * direction))
