from __future__ import annotations

from ...i18n import t
from ..platform import OperationResult


class CameraDependencies:
    """Checks the optional camera extras (OpenCV and MediaPipe)."""

    @staticmethod
    def check() -> OperationResult:
        try:
            import cv2  # noqa: F401
            import mediapipe  # noqa: F401
        except ImportError:
            return OperationResult.failure(t("camera.error.extra_missing"))
        return OperationResult.success()
