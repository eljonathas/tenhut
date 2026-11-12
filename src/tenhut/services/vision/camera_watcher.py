from __future__ import annotations

import math
import threading

from ...core import Clock, HeadPose
from ...i18n import t
from ..platform import OperatingSystem
from .capture_api import CaptureApi
from .face_landmark_model import FaceLandmarkModel
from .head_reading import HeadReading
from .head_reading_buffer import HeadReadingBuffer


class CameraWatcher(threading.Thread):
    """Reads camera frames on a thread and keeps the head pose estimated with MediaPipe."""

    FRAME_SIZE = (640, 480)
    READ_INTERVAL = 0.15
    PREVIOUS_CAMERA_WAIT = 3

    def __init__(
        self,
        device: int,
        model: FaceLandmarkModel,
        clock: Clock,
        *,
        system: OperatingSystem,
        wait_for: CameraWatcher | None = None,
    ) -> None:
        super().__init__(daemon=True, name="camera")
        self._device = device
        self._model = model
        self._clock = clock
        self._capture_api = CaptureApi.for_system(system)
        self._wait_for = wait_for
        self._running = True
        self._readings = HeadReadingBuffer(clock)
        self.error = ""
        self.ready = False

    def stop(self) -> None:
        self._running = False

    def angles(self) -> HeadPose | None:
        return self._readings.current()

    def last_seen(self) -> HeadReading | None:
        return self._readings.last_seen()

    def seen_since(self, timestamp: float) -> list[HeadReading]:
        return self._readings.seen_since(timestamp)

    def run(self) -> None:
        if self._wait_for is not None:
            self._wait_for.join(timeout=self.PREVIOUS_CAMERA_WAIT)
            self._wait_for = None
        resources = self._acquire() if self._running else None
        if resources is None:
            return
        capture, landmarker, libraries = resources
        self.ready = True
        try:
            self._read_loop(capture, landmarker, libraries)
        finally:
            capture.release()
            landmarker.close()

    def _acquire(self):
        """(capture, landmarker, libraries), or None with `error` set when the camera cannot be used."""
        try:
            import cv2
            import mediapipe as mp
            import numpy as np

            landmarker = self._create_landmarker()
            capture = self._open_capture(cv2)
        except (ImportError, OSError, RuntimeError, ValueError) as error:
            self.error = t("camera.error.unavailable", error=error)[:160]
            return None
        return None if capture is None else (capture, landmarker, (cv2, mp, np))

    def _create_landmarker(self):
        from mediapipe.tasks.python import BaseOptions, vision

        self._model.ensure()
        options = vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(self._model.path)),
            running_mode=vision.RunningMode.IMAGE,
            num_faces=1,
            output_facial_transformation_matrixes=True,
        )
        return vision.FaceLandmarker.create_from_options(options)

    def _open_capture(self, cv2):
        """The opened capture, or None (with `error` set) when the device cannot be opened."""
        capture = cv2.VideoCapture(self._device, getattr(cv2, self._capture_api.opencv_name, cv2.CAP_ANY))
        if not capture.isOpened():
            self.error = t(self._capture_api.open_error_key, n=self._device)
            return None
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.FRAME_SIZE[0])
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.FRAME_SIZE[1])
        return capture

    def _read_loop(self, capture, landmarker, libraries) -> None:
        cv2, mp, np = libraries
        while self._running:
            ok, frame = capture.read()
            if not ok:
                self._clock.sleep(0.3)
                continue
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            result = landmarker.detect(image)
            if result.facial_transformation_matrixes:
                rotation = np.array(result.facial_transformation_matrixes[0])[:3, :3]
                self._readings.store(self.pose_from_rotation(rotation))
            self._clock.sleep(self.READ_INTERVAL)

    @staticmethod
    def pose_from_rotation(rotation) -> HeadPose:
        """Yaw and pitch in degrees from the 3x3 rotation part of the face transformation matrix."""
        yaw = math.degrees(math.atan2(rotation[0, 2], rotation[2, 2]))
        pitch = math.degrees(math.asin(max(-1.0, min(1.0, -rotation[1, 2]))))
        return HeadPose(yaw, pitch)
