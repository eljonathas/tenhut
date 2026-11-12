from __future__ import annotations

from .apple_script import AppleScript
from .command_spec import CommandSpec
from .notifier import Notifier


class MacNotifier(Notifier):
    """Notifications through AppleScript."""

    def build_command(self, title: str, body: str, urgent: bool = False) -> CommandSpec:
        script = f"display notification {AppleScript.quote(body)} with title {AppleScript.quote(title)}"
        return CommandSpec(("osascript", "-e", script))
