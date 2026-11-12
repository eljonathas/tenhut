from __future__ import annotations

from .command_spec import CommandSpec
from .notifier import Notifier


class LinuxNotifier(Notifier):
    """Notifications through `notify-send`."""

    def build_command(self, title: str, body: str, urgent: bool = False) -> CommandSpec:
        level = "critical" if urgent else "normal"
        return CommandSpec(("notify-send", "-a", "Tenhut", "-u", level, title, body))
