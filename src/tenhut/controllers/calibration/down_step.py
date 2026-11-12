from __future__ import annotations

from tenhut.core import CalibrationRecorder, HeadPose
from tenhut.services.vision import HeadReading

from .calibration_step import CalibrationStep


class DownStep(CalibrationStep):
    """Looking down at the phone, which often takes the face out of the camera's picture."""

    MIN_DROP_DEGREES = 8
    MIN_SEEN_DROP_DEGREES = 4
    ASSUMED_DROP_DEGREES = 20
    tolerates_missing_face = True

    def rejection_key(self, pose: HeadPose, base: HeadPose | None) -> str | None:
        if abs(pose.pitch - base.pitch) < self.MIN_DROP_DEGREES:
            return "calibration.speech.pitch_too_small"
        return None

    def record(self, recorder: CalibrationRecorder, pose: HeadPose) -> None:
        recorder.record_down(pose)

    def record_vanished(self, recorder: CalibrationRecorder, seen: list[HeadReading]) -> None:
        """The face left the picture: the farthest pose seen on the way down counts, else MediaPipe's usual direction."""
        base = recorder.base
        farthest = max(seen, key=lambda reading: abs(reading.pose.pitch - base.pitch), default=None)
        if farthest and abs(farthest.pose.pitch - base.pitch) >= self.MIN_SEEN_DROP_DEGREES:
            pitch = farthest.pose.pitch
        else:
            pitch = base.pitch + self.ASSUMED_DROP_DEGREES
        recorder.record_down(HeadPose(base.yaw, pitch), face_vanishes=True)
