from __future__ import annotations

from dataclasses import dataclass, field, replace

from .block_group import BlockGroup
from .block_list import BlockList
from .camera_settings import CameraSettings
from .default_block_groups import DefaultBlockGroups
from .judge_settings import JudgeSettings
from .setting_value import SettingValue
from .sound_settings import SoundSettings
from .timer_settings import TimerSettings


@dataclass(frozen=True, slots=True)
class Settings:
    """Every user option. Loading merges a (possibly partial) dict over the defaults."""

    timer: TimerSettings = field(default_factory=TimerSettings)
    judge: JudgeSettings = field(default_factory=JudgeSettings)
    sound: SoundSettings = field(default_factory=SoundSettings)
    camera: CameraSettings = field(default_factory=CameraSettings)
    language: str = "auto"
    notifications_enabled: bool = True
    close_blocked_apps: bool = True
    block_groups: tuple[BlockGroup, ...] = field(default_factory=DefaultBlockGroups.create)

    @property
    def block_list(self) -> BlockList:
        return BlockList(self.block_groups)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Settings:
        """Unknown keys are ignored, bad values fall back to the default, and the user's groups replace the default ones."""
        defaults = cls()
        camera = data.get("camera")
        return cls(
            TimerSettings.from_dict(data),
            JudgeSettings.from_dict(data),
            SoundSettings.from_dict(data),
            CameraSettings.from_dict(camera if isinstance(camera, dict) else {}),
            SettingValue.text(data.get("language"), defaults.language) or defaults.language,
            SettingValue.flag(data.get("notifications_enabled"), defaults.notifications_enabled),
            SettingValue.flag(data.get("close_blocked_apps"), defaults.close_blocked_apps),
            cls._groups_from(data.get("block_groups"), defaults.block_groups),
        )

    @staticmethod
    def _groups_from(raw: object, default: tuple[BlockGroup, ...]) -> tuple[BlockGroup, ...]:
        if not isinstance(raw, dict):
            return default
        return tuple(
            BlockGroup(name, SettingValue.texts(group.get("domains")), SettingValue.texts(group.get("apps")))
            for name, group in raw.items()
            if isinstance(group, dict)
        )

    def to_dict(self) -> dict[str, object]:
        return {
            **self.timer.to_dict(),
            **self.judge.to_dict(),
            "language": self.language,
            **self.sound.to_dict(),
            "notifications_enabled": self.notifications_enabled,
            "close_blocked_apps": self.close_blocked_apps,
            "camera": self.camera.to_dict(),
            "block_groups": {g.name: g.to_dict() for g in self.block_groups},
        }

    def with_camera(self, camera: CameraSettings) -> Settings:
        return replace(self, camera=camera)
