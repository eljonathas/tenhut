from __future__ import annotations

from .command_runner import CommandRunner
from .linux_notifier import LinuxNotifier
from .mac_notifier import MacNotifier
from .notifier import Notifier
from .operating_system import OperatingSystem
from .windows_notifier import WindowsNotifier


class NotifierFactory:
    """Picks the notifier for the OS."""

    @staticmethod
    def create(system: OperatingSystem, runner: CommandRunner) -> Notifier:
        if system.is_windows:
            return WindowsNotifier(runner)
        return MacNotifier(runner) if system.is_mac else LinuxNotifier(runner)
