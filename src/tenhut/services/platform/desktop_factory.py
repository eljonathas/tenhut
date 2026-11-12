from __future__ import annotations

import os
from pathlib import Path

from .command_runner import CommandRunner
from .desktop_integration import DesktopIntegration
from .linux_desktop import LinuxDesktop
from .operating_system import OperatingSystem
from .unsupported_desktop import UnsupportedDesktop


class DesktopFactory:
    """Picks the desktop integration for the OS."""

    @staticmethod
    def create(system: OperatingSystem, runner: CommandRunner) -> DesktopIntegration:
        if not system.is_linux:
            return UnsupportedDesktop()
        data_home = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
        return LinuxDesktop(data_home, runner)
