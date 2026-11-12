from __future__ import annotations

from .desktop_command import DesktopCommand


class InstallDesktopCommand(DesktopCommand):
    """--install-desktop"""

    def run(self) -> int:
        return self._desktop().cli_install()
