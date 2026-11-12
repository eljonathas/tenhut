from __future__ import annotations

import sys
from enum import Enum


class OperatingSystem(Enum):
    """The systems the app supports, classified from `sys.platform`."""

    LINUX = "linux"
    MACOS = "macos"
    WINDOWS = "windows"

    @classmethod
    def of(cls, platform: str = sys.platform) -> OperatingSystem:
        """Anything that is not Windows or macOS counts as Linux."""
        if platform.startswith("win") or platform == "cygwin":
            return cls.WINDOWS
        return cls.MACOS if platform == "darwin" else cls.LINUX

    @classmethod
    def current(cls) -> OperatingSystem:
        return cls.of(sys.platform)

    @property
    def is_windows(self) -> bool:
        return self is OperatingSystem.WINDOWS

    @property
    def is_mac(self) -> bool:
        return self is OperatingSystem.MACOS

    @property
    def is_linux(self) -> bool:
        return self is OperatingSystem.LINUX
