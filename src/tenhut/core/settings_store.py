from __future__ import annotations

import json
import shutil
from pathlib import Path

from .legacy_settings_migration import LegacySettingsMigration
from .settings import Settings
from .settings_error import SettingsError


class SettingsStore:
    """Reads and writes the settings JSON file."""

    BACKUP_SUFFIX = ".bak-pt"

    def __init__(self, path: Path, migration: LegacySettingsMigration | None = None) -> None:
        self._path = path
        self._migration = migration or LegacySettingsMigration()

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> Settings:
        """Missing file: write and return the defaults. Corrupt file: the defaults, file untouched."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            settings = Settings()
            self.save(settings)
            return settings
        try:
            raw = self._read()
        except SettingsError:
            return Settings()
        if not self._migration.is_legacy(raw):
            return Settings.from_dict(raw)
        settings = Settings.from_dict(self._migration.migrate(raw))
        self._replace_legacy_file(settings)
        return settings

    def save(self, settings: Settings) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(settings.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self._path)

    def _read(self) -> dict[str, object]:
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise SettingsError(str(error)) from error
        if not isinstance(raw, dict):
            raise SettingsError("the settings file is not a JSON object")
        return raw

    def _replace_legacy_file(self, settings: Settings) -> None:
        backup = self._path.with_name(self._path.name + self.BACKUP_SUFFIX)
        try:
            if not backup.exists():
                shutil.copyfile(self._path, backup)
            self.save(settings)
        except OSError:
            pass  # read-only folder: the values are used anyway and the file is converted next time
