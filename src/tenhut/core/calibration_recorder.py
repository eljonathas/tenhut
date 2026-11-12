from __future__ import annotations

from .camera_calibration import CameraCalibration
from .head_pose import HeadPose
from .monitor_side import MonitorSide


class CalibrationRecorder:
    """Collects the poses of a calibration in progress until it is complete."""

    def __init__(self) -> None:
        self._base: HeadPose | None = None
        self._down: HeadPose | None = None
        self._sides: dict[MonitorSide, HeadPose] = {}
        self._down_face_vanishes = False

    @property
    def base(self) -> HeadPose | None:
        return self._base

    def record_base(self, pose: HeadPose) -> None:
        self._base = pose

    def record_down(self, pose: HeadPose, face_vanishes: bool = False) -> None:
        self._down = pose
        self._down_face_vanishes = face_vanishes

    def record_side(self, side: MonitorSide, pose: HeadPose) -> None:
        self._sides[side] = pose

    def is_complete(self) -> bool:
        return self._base is not None and self._down is not None

    def build(self) -> CameraCalibration:
        if self._base is None or self._down is None:
            raise ValueError("calibration is incomplete")
        return CameraCalibration(self._base, self._down, dict(self._sides), self._down_face_vanishes)
