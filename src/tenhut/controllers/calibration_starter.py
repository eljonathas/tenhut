from __future__ import annotations

from abc import ABC, abstractmethod


class CalibrationStarter(ABC):
    """Begins the camera calibration."""

    @abstractmethod
    def start(self) -> None: ...
