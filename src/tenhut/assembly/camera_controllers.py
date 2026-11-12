from __future__ import annotations

from dataclasses import dataclass

from tenhut.controllers import CalibrationController, CameraController, CameraHolder


@dataclass(frozen=True, slots=True)
class CameraControllers:
    """The camera thread owner, the posture watcher and the calibration."""

    holder: CameraHolder
    camera: CameraController
    calibration: CalibrationController
