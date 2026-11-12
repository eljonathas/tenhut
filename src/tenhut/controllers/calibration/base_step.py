from __future__ import annotations

from tenhut.core import CalibrationRecorder, HeadPose

from .calibration_step import CalibrationStep


class BaseStep(CalibrationStep):
    """Looking at the main screen."""

    def record(self, recorder: CalibrationRecorder, pose: HeadPose) -> None:
        recorder.record_base(pose)
