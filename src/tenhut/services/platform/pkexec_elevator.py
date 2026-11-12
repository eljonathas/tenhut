from __future__ import annotations

import shutil

from .command_spec import CommandSpec
from .elevator import Elevator


class PkexecElevator(Elevator):
    """Linux: polkit's graphical password prompt."""

    def command(self, script: str) -> CommandSpec | None:
        pkexec = shutil.which("pkexec")
        if not pkexec:
            return None
        return CommandSpec((pkexec, "/bin/sh", "-c", script), timeout=self.TIMEOUT_SECONDS)

    def cancelled(self, returncode: int, output_lower: str) -> bool:
        return "user canceled" in output_lower or "-128" in output_lower or returncode in (126, 127)
