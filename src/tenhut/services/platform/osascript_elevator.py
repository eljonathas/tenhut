from __future__ import annotations

from .apple_script import AppleScript
from .command_spec import CommandSpec
from .elevator import Elevator


class OsascriptElevator(Elevator):
    """macOS: the system administrator dialog."""

    def command(self, script: str) -> CommandSpec | None:
        source = f"do shell script {AppleScript.quote(script)} with administrator privileges"
        return CommandSpec(("osascript", "-e", source), timeout=self.TIMEOUT_SECONDS)

    def cancelled(self, returncode: int, output_lower: str) -> bool:
        return "user canceled" in output_lower or "-128" in output_lower
