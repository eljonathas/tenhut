from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from .operating_system import OperatingSystem

APP_DIR = "tenhut"


@dataclass(frozen=True, slots=True)
class AppPaths:
    """The three root folders and every file the app owns inside them."""

    config_root: Path
    state_root: Path
    data_root: Path

    @classmethod
    def detect(
        cls, platform: str = sys.platform, env: Mapping[str, str] | None = None, home: Path | None = None
    ) -> AppPaths:
        """`XDG_*_HOME`, when set and not empty, wins on every OS; otherwise the OS convention applies."""
        env = os.environ if env is None else env
        defaults = cls._defaults(OperatingSystem.of(platform), env, Path.home() if home is None else home)
        names = ("XDG_CONFIG_HOME", "XDG_STATE_HOME", "XDG_DATA_HOME")
        config, state, data = (Path(env[n]) if env.get(n) else d for n, d in zip(names, defaults))
        return cls(config, state, data)

    @staticmethod
    def _defaults(system: OperatingSystem, env: Mapping[str, str], home: Path) -> tuple[Path, Path, Path]:
        if system.is_windows:
            roaming = Path(env.get("APPDATA") or home / "AppData" / "Roaming")
            local = Path(env.get("LOCALAPPDATA") or home / "AppData" / "Local")
            return roaming, local, local
        if system.is_mac:
            support = home / "Library" / "Application Support"
            return support, support, support
        return home / ".config", home / ".local" / "state", home / ".local" / "share"

    @property
    def config_dir(self) -> Path:
        return self.config_root / APP_DIR

    @property
    def state_dir(self) -> Path:
        return self.state_root / APP_DIR

    @property
    def data_dir(self) -> Path:
        return self.data_root / APP_DIR

    @property
    def config_file(self) -> Path:
        return self.config_dir / "config.json"

    @property
    def session_file(self) -> Path:
        return self.state_dir / "state.json"

    @property
    def profile_file(self) -> Path:
        return self.state_dir / "profile.json"

    @property
    def request_log_file(self) -> Path:
        return self.state_dir / "requests.jsonl"

    @property
    def camera_model_file(self) -> Path:
        return self.data_dir / "face_landmarker.task"
