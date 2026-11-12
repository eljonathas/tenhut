from __future__ import annotations

from .desktop_command import DesktopCommand


class UninstallDesktopCommand(DesktopCommand):
    """--uninstall-desktop"""

    def run(self) -> int:
        return self._desktop().cli_uninstall()
