from __future__ import annotations

from enum import Enum


class PageId(Enum):
    """Every page the interface can show."""

    MAIN = "main"
    BOARD = "board"
    MISSION = "mission"
    REQUEST = "request"
    DESERTION = "desertion"
    SETTINGS = "settings"
    CALIBRATION = "calibration"
    CALIBRATION_TEST = "calibration_test"

    @property
    def is_calibration(self) -> bool:
        return self in (PageId.CALIBRATION, PageId.CALIBRATION_TEST)
