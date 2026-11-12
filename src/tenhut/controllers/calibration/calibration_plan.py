from __future__ import annotations

from .calibration_step import CalibrationStep


class CalibrationPlan:
    """The steps of a calibration and how far along it is."""

    def __init__(self, steps: list[CalibrationStep]) -> None:
        self._steps = steps
        self._index = 0

    @property
    def steps(self) -> list[CalibrationStep]:
        return self._steps

    @property
    def index(self) -> int:
        return self._index

    @property
    def current(self) -> CalibrationStep:
        return self._steps[self._index]

    @property
    def finished(self) -> bool:
        return self._index >= len(self._steps)

    def advance(self) -> None:
        self._index += 1
