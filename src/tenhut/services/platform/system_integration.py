from __future__ import annotations

import os
from pathlib import Path

from .command_error import CommandError
from .command_runner import CommandRunner
from .command_spec import CommandSpec
from .operating_system import OperatingSystem

APP_USER_MODEL_ID = "tenhut.app"


class SystemIntegration:
    """Small host-system services: administrator check, taskbar identity, opening files."""

    def __init__(self, system: OperatingSystem, runner: CommandRunner) -> None:
        self._system = system
        self._runner = runner

    def is_admin(self) -> bool:
        """Windows: is the process an administrator? Elsewhere: is it root?"""
        try:
            if self._system.is_windows:
                import ctypes

                return bool(ctypes.windll.shell32.IsUserAnAdmin())  # type: ignore[attr-defined]
            return os.geteuid() == 0
        except (AttributeError, OSError):
            return False

    def set_app_id(self) -> bool:
        """Windows: group the window and icon in the taskbar."""
        if not self._system.is_windows:
            return False
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)  # type: ignore[attr-defined]
            return True
        except (AttributeError, OSError):
            return False

    def open_command(self, path: str) -> CommandSpec | None:
        """None on Windows, where `os.startfile` is used instead."""
        if self._system.is_windows:
            return None
        return CommandSpec(("open" if self._system.is_mac else "xdg-open", path))

    def open_path(self, path: str | Path) -> bool:
        command = self.open_command(str(path))
        try:
            if command is None:
                os.startfile(str(path))  # type: ignore[attr-defined]
            else:
                self._runner.launch(command)
        except (AttributeError, OSError, CommandError):
            return False
        return True
