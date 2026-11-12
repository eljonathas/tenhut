from __future__ import annotations

from enum import Enum

from ..platform import OperatingSystem


class CaptureApi(Enum):
    """The OpenCV capture backend native to each OS, and the error text when the device cannot be opened."""

    DIRECTSHOW = ("CAP_DSHOW", "camera.error.cannot_open_device_index")
    AVFOUNDATION = ("CAP_AVFOUNDATION", "camera.error.cannot_open_device_index")
    V4L2 = ("CAP_V4L2", "camera.error.cannot_open_device_path")

    def __init__(self, opencv_name: str, open_error_key: str) -> None:
        self.opencv_name = opencv_name
        self.open_error_key = open_error_key

    @classmethod
    def for_system(cls, system: OperatingSystem) -> CaptureApi:
        if system.is_windows:
            return cls.DIRECTSHOW
        return cls.AVFOUNDATION if system.is_mac else cls.V4L2
