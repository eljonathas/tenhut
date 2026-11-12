from __future__ import annotations

from tenhut.core import CalibrationRecorder, HeadPose, MonitorSide

from .calibration_step import CalibrationStep


class SideStep(CalibrationStep):
    """Looking at a monitor beside the camera's."""

    MIN_TURN_DEGREES = 10

    def __init__(self, prompt: str, side: MonitorSide) -> None:
        super().__init__(prompt)
        self._side = side

    def rejection_key(self, pose: HeadPose, base: HeadPose | None) -> str | None:
        if abs(pose.yaw - base.yaw) < self.MIN_TURN_DEGREES:
            return "calibration.speech.yaw_too_small"
        return None

    def record(self, recorder: CalibrationRecorder, pose: HeadPose) -> None:
        recorder.record_side(self._side, pose)
