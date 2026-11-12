from __future__ import annotations

from .command_spec import CommandSpec
from .elevator import Elevator


class RootElevator(Elevator):
    """Already root: just run the script."""

    def command(self, script: str) -> CommandSpec | None:
        return CommandSpec(("/bin/sh", "-c", script), timeout=Elevator.TIMEOUT_SECONDS)
