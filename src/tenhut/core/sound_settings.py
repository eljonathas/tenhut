from __future__ import annotations

from dataclasses import dataclass

from .number_rule import NumberRule
from .setting_value import SettingValue


@dataclass(frozen=True, slots=True)
class SoundSettings:
    """Sound effects switch and master volume (percent)."""

    enabled: bool = True
    volume: int = 40

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> SoundSettings:
        default = cls()
        return cls(
            SettingValue.flag(data.get("sound_enabled"), default.enabled),
            NumberRule(default.volume, 0, 100).integer(data.get("volume")),
        )

    def to_dict(self) -> dict[str, object]:
        return {"sound_enabled": self.enabled, "volume": self.volume}
