from __future__ import annotations

from dataclasses import dataclass, replace

from .camera_calibration import CameraCalibration
from .number_rule import NumberRule
from .setting_value import SettingValue


@dataclass(frozen=True, slots=True)
class CameraSettings:
    """Camera surveillance options (off by default)."""

    enabled: bool = False
    device: int = 0
    camera_monitor: str = ""
    tolerance_seconds: float = 6
    down_threshold_degrees: float = 14
    side_threshold_degrees: float = 18
    penalty_minutes: float = 1
    calibration: CameraCalibration | None = None

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> CameraSettings:
        d = cls()
        return cls(
            SettingValue.flag(data.get("enabled"), d.enabled),
            NumberRule(d.device, 0, 64).integer(data.get("device")),
            SettingValue.text(data.get("camera_monitor"), d.camera_monitor),
            NumberRule(d.tolerance_seconds, 1, 120).real(data.get("tolerance_seconds")),
            NumberRule(d.down_threshold_degrees, 1, 90).real(data.get("down_threshold_degrees")),
            NumberRule(d.side_threshold_degrees, 1, 90).real(data.get("side_threshold_degrees")),
            NumberRule(d.penalty_minutes, 0, 60).real(data.get("penalty_minutes")),
            CameraCalibration.from_dict(data.get("calibration")),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "device": self.device,
            "camera_monitor": self.camera_monitor,
            "tolerance_seconds": self.tolerance_seconds,
            "down_threshold_degrees": self.down_threshold_degrees,
            "side_threshold_degrees": self.side_threshold_degrees,
            "penalty_minutes": self.penalty_minutes,
            "calibration": self.calibration.to_dict() if self.calibration else None,
        }

    def is_ready(self) -> bool:
        return self.enabled and self.calibration is not None

    def calibrated(self, calibration: CameraCalibration) -> CameraSettings:
        """A copy with the new calibration, and the surveillance switched on."""
        return replace(self, enabled=True, calibration=calibration)
