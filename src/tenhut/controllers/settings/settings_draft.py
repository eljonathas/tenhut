from __future__ import annotations

from tenhut.core import Settings

from .setting_key import SettingKey


class SettingsDraft:
    """The settings being edited; nothing is in force until the user saves."""

    def __init__(self, values: dict[str, object]) -> None:
        self._values = values
        self._revision = 0

    @classmethod
    def from_settings(cls, settings: Settings) -> SettingsDraft:
        return cls(settings.to_dict())

    @property
    def revision(self) -> int:
        """Grows with every edit, so derived data can tell when to be recomputed."""
        return self._revision

    @property
    def has_camera_calibration(self) -> bool:
        return bool(self._section(("camera",))["calibration"])

    def get(self, key: SettingKey) -> object:
        return self._section(key.path[:-1])[key.path[-1]]

    def set(self, key: SettingKey, value: object) -> None:
        self._section(key.path[:-1])[key.path[-1]] = value
        self._revision += 1

    def as_settings(self) -> Settings:
        return Settings.from_dict(self._values)

    def merged_into(self, base: Settings) -> Settings:
        """``base`` with every edited value applied over it."""
        return Settings.from_dict({**base.to_dict(), **self._values})

    def keeping_unlocked(self, base: Settings) -> SettingsDraft:
        """``base`` plus only the edits that are allowed during a combat."""
        kept = {key.path[0]: self._values[key.path[0]] for key in SettingKey if key.always_unlocked}
        return SettingsDraft({**base.to_dict(), **kept})

    def _section(self, path: tuple[str, ...]) -> dict[str, object]:
        node = self._values
        for part in path:
            node = node[part]
        return node
