from __future__ import annotations

from abc import ABC, abstractmethod

from tenhut.core import CalibrationRecorder, HeadPose


class CalibrationStep(ABC):
    """One pose the soldier is asked to hold during the calibration."""

    tolerates_missing_face = False

    def __init__(self, prompt: str) -> None:
        self._prompt = prompt

    @property
    def prompt(self) -> str:
        return self._prompt

    def rejection_key(self, pose: HeadPose, base: HeadPose | None) -> str | None:
        """The translation key explaining why ``pose`` is unusable, or None when it is fine."""
        return None

    @abstractmethod
    def record(self, recorder: CalibrationRecorder, pose: HeadPose) -> None: ...
