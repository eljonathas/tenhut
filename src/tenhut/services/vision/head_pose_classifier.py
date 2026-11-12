from __future__ import annotations

from ...core import CameraCalibration, CameraSettings, HeadPose
from .gaze_state import GazeState
from .head_reading import HeadReading


class HeadPoseClassifier:
    """Decides the gaze state of a head pose against the user's calibration.

    Looking sideways is only allowed toward a side where a monitor exists; looking down is always an
    infraction. The calibration removes sign ambiguities (mirrored image, tilted camera, a lower monitor).
    """

    MISSING_MEMORY_SECONDS = 12.0
    MIN_DOWN_TRAVEL = 6.0
    MIN_SIDE_TRAVEL = 8.0
    LOST_DOWN_FRACTION = 0.35
    MIN_DOWN_THRESHOLD = 7.0
    DOWN_THRESHOLD_SHARE = 0.55

    def __init__(self, calibration: CameraCalibration, settings: CameraSettings) -> None:
        self._calibration = calibration
        self._down_threshold = float(settings.down_threshold_degrees)
        self._side_threshold = float(settings.side_threshold_degrees)

    def _down_direction(self) -> tuple[int, float]:
        """(sign of "down" along the pitch axis, threshold in degrees)."""
        travel = self._calibration.down.pitch - self._calibration.base.pitch
        threshold = self._down_threshold
        if abs(travel) >= self.MIN_DOWN_TRAVEL:
            # a short calibrated drop must not be demanded to travel further than it did
            threshold = max(self.MIN_DOWN_THRESHOLD, min(threshold, self.DOWN_THRESHOLD_SHARE * abs(travel)))
        return (1 if travel >= 0 else -1), threshold

    def classify_missing(self, last_seen: HeadReading | None, now: float) -> GazeState | None:
        """The face vanished. Right after the head started to drop it is the phone (DOWN); otherwise absence (None).

        Looking down often takes the face out of the picture, so "vanished while going down" counts as looking down.
        """
        if last_seen is None or now - last_seen.timestamp > self.MISSING_MEMORY_SECONDS:
            return None
        sign, threshold = self._down_direction()
        dropped = (last_seen.pose.pitch - self._calibration.base.pitch) * sign
        return GazeState.DOWN if dropped > self.LOST_DOWN_FRACTION * threshold else None

    def classify(self, pose: HeadPose) -> GazeState:
        base = self._calibration.base
        yaw_offset = pose.yaw - base.yaw
        sign, down_threshold = self._down_direction()
        state, reference_pitch = GazeState.OK, base.pitch
        if abs(yaw_offset) > self._side_threshold:
            sample = self._side_monitor_pose(yaw_offset)
            if sample is None:
                return GazeState.SIDE
            state, reference_pitch = GazeState.SIDE_ALLOWED, sample.pitch  # a side monitor may sit lower or higher
        return GazeState.DOWN if (pose.pitch - reference_pitch) * sign > down_threshold else state

    def _side_monitor_pose(self, yaw_offset: float) -> HeadPose | None:
        """The calibrated side pose in the direction the head turned, if there is one."""
        for sample in self._calibration.sides.values():
            offset = sample.yaw - self._calibration.base.yaw
            if abs(offset) >= self.MIN_SIDE_TRAVEL and (offset > 0) == (yaw_offset > 0):
                return sample
        return None
