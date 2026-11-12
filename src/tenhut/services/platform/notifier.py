from __future__ import annotations

import contextlib
from abc import ABC, abstractmethod

from .command_error import CommandError
from .command_runner import CommandRunner
from .command_spec import CommandSpec


class Notifier(ABC):
    """Shows a system notification without blocking and without ever raising."""

    def __init__(self, runner: CommandRunner) -> None:
        self._runner = runner

    @abstractmethod
    def build_command(self, title: str, body: str, urgent: bool = False) -> CommandSpec:
        """The command that shows the notification."""

    def notify(self, title: str, body: str, urgent: bool = False) -> None:
        with contextlib.suppress(CommandError):
            self._runner.launch(self.build_command(title, body, urgent))
