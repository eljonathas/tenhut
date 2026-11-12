from __future__ import annotations

from abc import ABC, abstractmethod


class CameraStopListener(ABC):
    """Told when the camera is switched off."""

    @abstractmethod
    def camera_stopped(self) -> None: ...
